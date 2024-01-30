from typing import NamedTuple, List, Tuple, Dict

from algorithm_types import BinHeuristicType
from items_type import Bin, Item
from packing_algorithm import PackingAlgorithm

SkylineSegment = NamedTuple('SkylineSegment', [('x', int),
                                               ('y', int),
                                               ('width', int)])


class SkylineAlgorithm(PackingAlgorithm):

    def __init__(self, rotation: bool, heuristic: BinHeuristicType):
        super().__init__(rotation, heuristic)
        self.bin_skyline: Dict[str, {SkylineSegment, List[SkylineSegment]}] = {}

    @staticmethod
    def _clip_segment(segment: SkylineSegment, item: Item) -> List[SkylineSegment]:
        """
        Clip out the length of segment adjacent to the item.
        Return the rest.
        """
        # Segment not under new item
        itemx = item.x
        item_end_x = itemx + item.width
        segx = segment.x
        seg_end_x = segx + segment.width
        if segx > item_end_x or seg_end_x < itemx:
            return [segment]
        # Segment fully under new item
        elif segx >= itemx and seg_end_x <= item_end_x:
            return []
        # Segment partially under new item (to the left)
        elif segx < itemx and seg_end_x <= item_end_x:
            new_segment = SkylineSegment(segx, segment.y, itemx - segx)
            return [new_segment]
        # Segment partially under new item (to the right)
        elif segx >= itemx and seg_end_x > item_end_x:
            new_segment = SkylineSegment(item_end_x,
                                         segment.y,
                                         seg_end_x - item_end_x)
            return [new_segment]
        # Segment wider than item in both directions
        elif segx < itemx and seg_end_x > item_end_x:
            new_segment_left = SkylineSegment(segx,
                                              segment.y,
                                              itemx - segx)
            new_segment_right = SkylineSegment(item_end_x,
                                               segment.y,
                                               seg_end_x - item_end_x)
            return [new_segment_left, new_segment_right]
        else:
            return []

    def _update_segment(self, bin: Bin, segment: SkylineSegment, y: int, item: Item) -> List[SkylineSegment]:
        """
        Clips the line segment under the new item and returns
        an updated skyline segment list.
        """
        new_segments = []
        for seg in self.bin_skyline[bin.id]['skyline']:
            new_segments.extend(self._clip_segment(seg, item))

        if len(new_segments) != 0:
            new_segments = sorted(new_segments, key=lambda seg: (seg.x, seg.y, seg.width))

        # Create new segment if room above item
        if item.height + item.y < bin.height:
            new_seg_y = item.y + item.height
            new_seg = SkylineSegment(segment.x, new_seg_y, item.width)
            new_segments.append(new_seg)
            new_segments = sorted(new_segments, key=lambda seg: (seg.x, seg.y, seg.width))

        return new_segments

    def _merge_segments(self, bin: Bin) -> None:
        """
        Merge any adjacent SkylineSegments
        """
        new_segments = [self.bin_skyline[bin.id]['skyline'][0]]
        for seg in self.bin_skyline[bin.id]['skyline'][1:]:
            last = new_segments[-1]
            if seg.y == last.y and seg.x == last.x + last.width:
                new_last = SkylineSegment(last.x, last.y,
                                          (seg.x + seg.width) - last.x)
                new_segments.remove(last)
                new_segments.append(new_last)
                continue
            new_segments.append(seg)

        new_segments = sorted(new_segments, key=lambda seg: (seg.x, seg.y, seg.width))
        self.bin_skyline[bin.id]['skyline'] = new_segments

    def _check_fit(self, item_width: int,
                   item_height: int,
                   sky_index: int, bin: Bin) -> tuple[bool, None]:
        """
        Returns true if the item will fit above the skyline
        segment sky_index. Also works if the item is wider
        then the segment.
        """
        i = sky_index
        x = self.bin_skyline[bin.id]['skyline'][i].x
        y = self.bin_skyline[bin.id]['skyline'][i].y
        width = item_width

        if x + item_width > bin.width:
            return (False, None)
        if y + item_height > bin.height:
            return (False, None)

        while width > 0:
            y = max(y, self.bin_skyline[bin.id]['skyline'][i].y)
            if y + item_height > bin.height:
                return (False, None)
            width -= self.bin_skyline[bin.id]['skyline'][i].width
            i += 1
            if width > 0 and i == len(self.bin_skyline[bin.id]['skyline']):
                return (False, None)
        return (True, y)

    def initialize_bin(self, bin: Bin) -> None:
        """
        Initialize a bin with an empty list of shelves and full available height.

        :param bin: Bin to be initialized.
        """
        starting_segment = SkylineSegment(0, 0, bin.width)
        self.bin_skyline[bin.id] = {'starting_segment': starting_segment, 'skyline': [starting_segment]}

    def pack_item(self, bin: Bin, item: Item) -> bool:
        """
        Wrapper for insertion heuristics
        """
        if bin.id not in self.bin_skyline:
            self.initialize_bin(bin)

        _, best_seg, rotation, best_y = self._find_best_score(bin, item)
        if best_seg:
            if rotation:
                item.rotate()
            item.x, item.y = (best_seg.x, best_y)
            bin.items.append(item)
            self.bin_skyline[bin.id]['skyline'] = self._update_segment(bin, best_seg, best_y, item)
            self._merge_segments(bin)
            return True
        return False

    @staticmethod
    def calc_waste(segs: List[SkylineSegment],
                   item: Item,
                   y: int,
                   i: int,
                   rotation: bool = False) -> int:
        """
        Returns the total wasted area if item is
        inserted above segment
        """
        wasted_area = 0
        item_left = segs[i].x
        if not rotation:
            item_right = item_left + item.width
        else:
            item_right = item_left + item.height
        for seg in segs[i:]:
            if seg.x >= item_right or seg.x + seg.width <= item_left:
                break
            left_side = seg.x
            right_side = min(item_right, seg.x + seg.width)
            wasted_area += (right_side - left_side) * (y - seg.y)
        return wasted_area

    def _score(self, segs: List[SkylineSegment], item: Item, y: int, i: int, bin: Bin,
               rotation: bool = False) -> float:
        """
        Calculate the score for a given item placement. Based on the heuristic
        """
        if self.heuristic == BinHeuristicType.next_fit or self.heuristic == BinHeuristicType.first_fit:
            return i  # Lower index has higher priority

        elif self.heuristic == BinHeuristicType.best_area_fit or self.heuristic == BinHeuristicType.worst_area_fit:
            waste = self.calc_waste(segs, item, y, i, rotation)
            return bin.remaining_area - waste

        elif self.heuristic == BinHeuristicType.best_width_fit or self.heuristic == BinHeuristicType.worst_width_fit:
            return abs(segs[i].width - (item.width if not rotation else item.height))

        elif self.heuristic == BinHeuristicType.best_height_fit or self.heuristic == BinHeuristicType.worst_height_fit:
            return abs(segs[i].y - (item.height if not rotation else item.width))

        else:
            return 0.0

    def _find_best_score(self, bin: Bin, item: Item) -> Tuple[int, SkylineSegment, int, bool]:
        segs = []
        for i, segment in enumerate(self.bin_skyline[bin.id]['skyline']):
            fits, y = self._check_fit(item.width, item.height, i, bin)
            if fits:
                score = self._score(self.bin_skyline[bin.id]['skyline'], item, y, i, bin)
                segs.append((score, segment, y, False))
            if self.rotation:
                fits, y = self._check_fit(item.height, item.width, i, bin)
                if fits:
                    score = self._score(self.bin_skyline[bin.id]['skyline'], item, y, i, bin, rotation=True)
                    segs.append((score, segment, y, True))
        try:
            if self.heuristic in [BinHeuristicType.worst_height_fit, BinHeuristicType.worst_width_fit, BinHeuristicType.worst_area_fit]:
                _score, seg, y, rot = min(segs, key=lambda x: x[0])
            else:
                _score, seg, y, rot = max(segs, key=lambda x: x[0])
            return _score, seg, rot, y
        except ValueError:
            return None, None, None, False

    def evaluate_bin(self, bin: Bin, item: Item) -> float:
        """
        Evaluate and score a bin based on the given heuristic.

        :param bin: The bin to evaluate.
        :param item: The item to be placed.
        :return: A score indicating the bin's suitability.
        """
        fits, _ = self.check_item_fit(bin, item)
        best_score = 0
        if not fits:
            return best_score

        best_score, _, _, _ = self._find_best_score(bin, item)

        return best_score

    def find_best_bin(self, bins: List[Bin], item: Item) -> Bin:
        best_bin, best_score = None, 0

        for bin in bins:
            score = self.evaluate_bin(bin, item)
            if score is None:
                continue
            if score > best_score:
                best_bin, best_score = bin, score
            # if best_score == 1:
            #     return best_bin

        return best_bin

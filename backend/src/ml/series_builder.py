from typing import Any, Dict, List, Optional


class SeriesBuilder:
    def build(
        self,
        current_item: Dict[str, Any],
        series_items: List[Dict[str, Any]],
        detection: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build ordered reading guide for a series."""
        current_id = current_item.get("content_id")
        current_pos = detection.get("position")
        series_name = detection.get("series_name") or "Unknown Series"

        all_items = {current_id: current_item}
        for item in series_items:
            cid = item.get("content_id")
            if cid:
                all_items[cid] = item

        def sort_key(item):
            pos = item.get("position")
            if item.get("content_id") == current_id:
                pos = current_pos
            title = item.get("title") or ""
            return (pos if pos is not None else 999999, title)

        sorted_list = sorted(all_items.values(), key=sort_key)

        items_out = []
        for item in sorted_list:
            cid = item.get("content_id")
            item_pos = item.get("position")
            if cid == current_id:
                item_pos = current_pos

            label = self._get_label(cid, current_id, item_pos, current_pos)

            items_out.append({
                "content_id": cid,
                "title": item.get("title"),
                "position": item_pos,
                "label": label,
            })

        return {
            "series_name": series_name,
            "total": len(items_out),
            "current_position": current_pos,
            "items": items_out,
        }

    def _get_label(
        self,
        item_id: str,
        current_id: str,
        item_pos: Optional[int],
        current_pos: Optional[int],
    ) -> str:
        if item_id == current_id:
            return "You Are Here"

        if item_pos is None or current_pos is None:
            return "Also In This Series"

        if item_pos < current_pos:
            return "Read This First"

        if item_pos == current_pos + 1:
            return "Read This Next"

        if item_pos > current_pos + 1:
            return "Coming Up"

        return "Also In This Series"
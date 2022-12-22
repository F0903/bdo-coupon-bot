from itertools import chain
from typing import Tuple
from bdo_coupon_scanner.scanners.site_scanner import OfficialSiteScanner
from bdo_coupon_scanner.scanners.twitter_scanner import TwitterScanner
from time import perf_counter
from ..db import DatabaseTransaction
from ..db.coupons import Coupon


def remove_duplicates_by_key(selector, items):
    history = []
    for x in items:
        key = selector(x)
        seen = False
        for old_key in history:
            if key != old_key:
                continue
            seen = True
        if seen:
            continue
        history.append(key)
        yield x


async def get_new_codes(save_to_db: bool) -> Tuple[list[Coupon], float]:
    start_t = perf_counter()

    site_codes = OfficialSiteScanner().get_codes()
    twitter_codes = TwitterScanner().get_codes()

    combined_codes = chain(site_codes, twitter_codes)
    codes = remove_duplicates_by_key(lambda x: x.code, combined_codes)

    delta_codes = []
    with DatabaseTransaction() as db:
        existing_codes = list(
            db.coupons.get_all()
        )  # Must be a list as an iterator would get exhausted on first pass.
        for new_code in codes:
            exists = False
            for old_code in existing_codes:
                if new_code.code != old_code.code:
                    continue
                exists = True
                break
            if not exists:
                if save_to_db:
                    db.coupons.add(new_code)
                delta_codes.append(new_code)
    end_t = perf_counter()
    elapsed_s = round(end_t - start_t, 2)
    return delta_codes, elapsed_s

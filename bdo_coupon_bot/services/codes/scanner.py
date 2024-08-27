import logging
from itertools import chain
from typing import Tuple
from bdo_coupon_scanner.scanners.site_scanner import OfficialSiteScanner
from bdo_coupon_scanner.scanners.garmoth_scanner import GarmothScanner
from time import perf_counter
from ..db import DatabaseTransaction
from ..db.tables.coupons import Coupon


class ScannerException(Exception):
    pass


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
    log = logging.getLogger(__name__)
    start_t = perf_counter()

    codes = []
    try:
        site_codes = OfficialSiteScanner().get_codes()
        codes = chain(codes, site_codes)
        log.debug(f"Site codes: {site_codes}")
    except Exception:
        log.error("Could not get site codes!")

    try:
        log.debug(f"Code chain before 2 scan: {codes}")
        garmoth_codes = GarmothScanner().get_codes()
        codes = chain(codes, garmoth_codes)
        log.debug(f"Twitter codes: {garmoth_codes}")
    except Exception:
        log.error("Could not get garmoth codes!")

    codes = remove_duplicates_by_key(lambda x: x.code, codes)

    delta_codes = []
    with DatabaseTransaction() as db:
        if db.subscribers.count() < 1:
            log.error("No channels are subscribed!")
            raise ScannerException("Cannot send codes. No channels are subscribed!")
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

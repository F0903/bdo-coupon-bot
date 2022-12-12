from itertools import chain
from bdo_coupon_scanner.site_checker import OfficialSiteChecker
from bdo_coupon_scanner.twitter_checker import TwitterChecker
from ..db import ScannerDb, CouponCode


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


async def get_new_codes() -> list[CouponCode]:
    site_codes = map(
        lambda x: CouponCode(x.code, x.date), OfficialSiteChecker().get_codes()
    )
    twitter_codes = map(
        lambda x: CouponCode(x, None),
        TwitterChecker().get_codes(),
    )

    code_chain = chain(site_codes, twitter_codes)
    combined_codes = remove_duplicates_by_key(lambda x: x.code, code_chain)

    delta_codes = []
    with ScannerDb() as db:
        existing_codes = db.coupons.get_all()
        for new_code in combined_codes:
            exists = False
            for old_code in existing_codes:
                if new_code.code != old_code.code:
                    continue
                exists = True
                break
            if not exists:
                db.coupons.add(new_code)
                delta_codes.append(new_code)

    return delta_codes

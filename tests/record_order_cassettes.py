"""시장가 매수→매도 VCR cassette 녹화 스크립트.

실제 거래가 발생하므로 소량의 금전적 손실(스프레드+수수료)이 발생한다.
KRW-BTC 마켓에서 10,000원으로 매수 후 즉시 전량 매도한다.

사용법:
    UPBIT_ACCESS_KEY=xxx UPBIT_SECRET_KEY=yyy \
        uv run python tests/record_order_cassettes.py
"""

from __future__ import annotations

import os
import sys
import time

from tests._vcr import upbeat_vcr
from upbeat import Upbeat

_MARKET = "KRW-BTC"
_BUY_AMOUNT = "10000"  # 매도 시 최소금액(5000원) 확보를 위해 넉넉히
_CASSETTE_PATH = "orders/market_buy_sell.yaml"


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    return value


def main() -> None:
    access_key = _require_env("UPBIT_ACCESS_KEY")
    secret_key = _require_env("UPBIT_SECRET_KEY")

    print("=" * 60)
    print("시장가 매수→매도 VCR Cassette 녹화")
    print("=" * 60)
    print(f"  마켓: {_MARKET}")
    print(f"  매수 금액: {_BUY_AMOUNT}원")
    print("  예상 손실: 스프레드 + 수수료 ≈ 100~200원")
    print(f"  Cassette: {_CASSETTE_PATH}")
    print("=" * 60)
    print()

    confirm = input("계속하시겠습니까? (y/N): ").strip().lower()
    if confirm != "y":
        print("취소되었습니다.")
        sys.exit(0)

    client = Upbeat(
        access_key=access_key,
        secret_key=secret_key,
        max_retries=0,
        auto_throttle=False,
    )

    with client, upbeat_vcr.use_cassette(
        _CASSETTE_PATH, record_mode="all"
    ):
        # 1) 시장가 매수
        print(f"\n[1/4] 시장가 매수 ({_MARKET}, {_BUY_AMOUNT}원)...")
        buy = client.orders.create(
            market=_MARKET,
            side="bid",
            ord_type="price",
            price=_BUY_AMOUNT,
        )
        print(f"  주문 생성: uuid={buy.uuid}, state={buy.state}")

        # 체결 대기
        time.sleep(1)

        # 2) 매수 주문 상태 조회
        print("[2/4] 매수 주문 상태 조회...")
        buy_detail = client.orders.get(uuid=buy.uuid)
        print(
            f"  state={buy_detail.state}, "
            f"executed_volume={buy_detail.executed_volume}"
        )

        if buy_detail.executed_volume == "0":
            print("ERROR: 매수 체결량이 0입니다. 매도를 건너뜁니다.")
            sys.exit(1)

        # 3) 매수 수량 전량 시장가 매도
        print(f"[3/4] 시장가 매도 (volume={buy_detail.executed_volume})...")
        try:
            sell = client.orders.create(
                market=_MARKET,
                side="ask",
                ord_type="market",
                volume=buy_detail.executed_volume,
            )
            print(f"  주문 생성: uuid={sell.uuid}, state={sell.state}")
        except Exception as e:
            print(f"ERROR: 매도 실패 — {e}")
            print("  수동으로 매도해야 합니다!")
            sys.exit(1)

        # 체결 대기
        time.sleep(1)

        # 4) 매도 주문 상태 조회
        print("[4/4] 매도 주문 상태 조회...")
        sell_detail = client.orders.get(uuid=sell.uuid)
        print(
            f"  state={sell_detail.state}, "
            f"executed_volume={sell_detail.executed_volume}"
        )

    print(f"\nCassette 저장 완료: tests/cassettes/{_CASSETTE_PATH}")
    print("녹화가 완료되었습니다.")


if __name__ == "__main__":
    main()

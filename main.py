import argparse

from application_log import build_score_vs_outcome_report, load_applications
from career_radar import build_daily_radar_message
from config import get_settings
from telegram_notifier import TelegramNotifier


def test_telegram() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        raise SystemExit(
            "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. "
            "Set them as environment variables or GitHub Secrets."
        )

    notifier = TelegramNotifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )
    notifier.send_message(build_daily_radar_message())


def main() -> None:
    parser = argparse.ArgumentParser(description="Abdullah Career Agent")
    parser.add_argument("--test-telegram", action="store_true")
    parser.add_argument(
        "--review-applications",
        nargs="?",
        const="applications.csv",
        metavar="CSV",
        help="Compare the bot's scores with replies you got (default: applications.csv)",
    )
    args = parser.parse_args()

    if args.test_telegram:
        test_telegram()
        return

    if args.review_applications:
        print(build_score_vs_outcome_report(load_applications(args.review_applications)))
        return

    parser.print_help()


if __name__ == "__main__":
    main()

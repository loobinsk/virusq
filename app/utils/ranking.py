from app.typings.literals import RankingsTypeLiteral, RankingsPeriodLiteral


def get_ranking_field(
    ranking_type: RankingsTypeLiteral,
    ranking_period: RankingsPeriodLiteral,
):
    if ranking_type == "game":
        if ranking_period == "alltime":
            field = "game_alltime_highscore"
        elif ranking_period == "daily":
            field = "game_daily_highscore"
        else:
            raise NotImplementedError

    elif ranking_type == "overall_profit":
        if ranking_period == "alltime":
            field = "balance"
        elif ranking_period == "daily":
            field = "daily_overall_profit"
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    return field

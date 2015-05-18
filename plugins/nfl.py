import plugintypes
import nflgame

class NflPlugin(plugintypes.TelegramPlugin):
    """
    Print and query NFL stats using the nflgame library
    """
    MAX_COUNT = 20
    DEFAULT_COUNT = 5


    patterns = [
        "^!top([0-9]+)? ([0-9]+)? ?([a-zA-Z]*) ?([0-9]{2,4}) ?(week=([0-9]{1,2}))?"
    ]

    usage = [
        "!top [n] role [year] [week=x]: Print the top n position for the "
        "season. \nRoles: rushing, passing, receiving, fumbles, kicking, "
        "punting, kickret, puntret, defense, penalty, touchdowns",
    ]

    roles = ["rushing", "passing", "receiving", "fumbles", "kicking", "punting", 
             "kickret", "puntret", "defense", "penalty", "touchdowns"]

    def run(self, msg, matches):
        if matches.group(0).startswith("!top"):
            return stats_top(matches.group(1), matches.group(2), matches.group(3), matches.group(5))

    def stats_top(self, count, role, year, count, week):
        if role not in roles:
            return "Role not valid, must be one of :\n{0}".formate(",".join(roles))

        if count is None:
            count = DEFAULT_COUNT
        elif count > MAX_LIST:
            count = MAX_LIST

        if year is None:
            year = 2014 # TODO be dynamic

        if week is None:
            games = nflgame.games(year)
        else:
            games = nflgame.games(year, week=week)
            
        players = nflgame.combine_game_stats(games)
        

        text = "Top {role} leaders:\n".format(role=role)
        for p in get_role(players, role, count):
            text += "{player} {carries} carries for {yards} yds and {tds} TDs"
                    "".format(player=p, carries=p.rushing_att, 
                              yards=p.rushing_yds, tds=p.rushing_tds)


        return text


    def get_role(self, players, role, count):
        return {
            "rushing": players.rushing().sort('rushing_yds').limit(count),
          "passing": players.passing().sort('passing_att').limit(count),
            "receiving": players.rushing().sort('rushing_yds').limit(count),
            "fumbles": players.rushing().sort('rushing_yds').limit(count),
            "kicking": players.rushing().sort('rushing_yds').limit(count),
            "punting": players.rushing().sort('rushing_yds').limit(count),
            "kickret": players.rushing().sort('rushing_yds').limit(count),
            "puntret": players.rushing().sort('rushing_yds').limit(count),
            "defense": players.rushing().sort('rushing_yds').limit(count),
            "penalty": players.rushing().sort('rushing_yds').limit(count),
            "touchdowns": players.rushing().sort('rushing_yds').limit(count),
        }[role]       
             
      

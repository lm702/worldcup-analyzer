"""
预置球队数据: 基于2026世界杯真实公布的26人大名单
"""
from core.models import Squad, Player, Position


def _p(name: str, pos: str, club: str, age: int, caps: int = 0, goals: int = 0,
       depth: int = 2, rating: float = 6.5, star: bool = False, yc: int = 0) -> Player:
    return Player(
        name=name, position=Position(pos), club=club, age=age,
        caps=caps, goals=goals, depth_rank=depth, season_rating=rating,
        is_star=star, yellow_cards_24=yc,
    )


def brazil_squad() -> Squad:
    return Squad(team_name="巴西", group="C", coach="Carlo Ancelotti", players=[
        _p("Alisson", "GK", "Liverpool", 33, 70, 0, 1, 8.5, True),
        _p("Ederson", "GK", "Fenerbahçe", 32, 25, 0, 2, 8.0, True),
        _p("Weverton", "GK", "Grêmio", 38, 10, 0, 3, 6.5),
        _p("Marquinhos", "CB", "PSG", 32, 90, 7, 1, 8.0, True, yc=4),
        _p("Gabriel Magalhães", "CB", "Arsenal", 27, 35, 4, 1, 8.0, star=True, yc=5),
        _p("Bremer", "CB", "Juventus", 28, 20, 2, 2, 7.5, yc=6),
        _p("Ibañez", "CB", "Al-Ahli", 26, 15, 1, 2, 6.5, yc=3),
        _p("Léo Pereira", "CB", "Flamengo", 29, 8, 0, 3, 6.0),
        _p("Danilo", "RB", "Flamengo", 34, 60, 2, 2, 6.5, yc=4),
        _p("Wesley", "RB", "Roma", 22, 10, 1, 2, 7.0, yc=3),
        _p("Alex Sandro", "LB", "Flamengo", 35, 45, 2, 2, 6.5, yc=3),
        _p("Douglas Santos", "LB", "Zenit", 31, 20, 1, 2, 6.5),
        _p("Bruno Guimarães", "CM", "Newcastle", 27, 30, 3, 1, 8.5, True, yc=5),
        _p("Casemiro", "DM", "Manchester United", 34, 75, 7, 2, 6.5, star=True, yc=8),
        _p("Fabinho", "DM", "Al-Ittihad", 32, 35, 2, 2, 6.0, yc=5),
        _p("Lucas Paquetá", "AM", "Flamengo", 27, 48, 12, 2, 7.5, star=True, yc=4),
        _p("Danilo Santos", "CM", "Botafogo", 25, 5, 0, 3, 6.0),
        _p("Vinícius Júnior", "LW", "Real Madrid", 25, 40, 15, 1, 9.0, True, yc=3),
        _p("Raphinha", "RW", "Barcelona", 28, 30, 10, 1, 8.0, True, yc=2),
        _p("Gabriel Martinelli", "LW", "Arsenal", 23, 18, 5, 2, 7.5, yc=2),
        _p("Neymar", "LW", "Santos", 34, 128, 79, 2, 7.0, True, yc=2),
        _p("Matheus Cunha", "ST", "Manchester United", 26, 15, 6, 2, 7.0, yc=3),
        _p("Igor Thiago", "ST", "Brentford", 24, 8, 3, 2, 7.0, yc=2),
        _p("Endrick", "ST", "Lyon", 19, 6, 2, 3, 7.5, star=True),
        _p("Rayan", "ST", "Bournemouth", 20, 4, 1, 3, 6.5),
        _p("Luiz Henrique", "RW", "Zenit", 24, 10, 2, 3, 6.5),
    ])


def scotland_squad() -> Squad:
    return Squad(team_name="苏格兰", group="C", coach="Steve Clarke", players=[
        _p("Craig Gordon", "GK", "Hearts", 43, 70, 0, 3, 6.0),
        _p("Angus Gunn", "GK", "Nottingham Forest", 30, 15, 0, 1, 6.5),
        _p("Liam Kelly", "GK", "Rangers", 30, 5, 0, 3, 6.0),
        _p("Andy Robertson", "LB", "Liverpool", 32, 75, 3, 1, 8.5, True, yc=3),
        _p("Kieran Tierney", "LB", "Celtic", 29, 50, 2, 2, 7.5, yc=4),
        _p("Aaron Hickey", "RB", "Brentford", 23, 20, 1, 1, 7.5, star=True, yc=3),
        _p("Nathan Patterson", "RB", "Everton", 24, 15, 0, 2, 6.5, yc=3),
        _p("Anthony Ralston", "RB", "Celtic", 27, 12, 1, 3, 6.0),
        _p("Grant Hanley", "CB", "Hibernian", 34, 55, 2, 2, 6.5, yc=5),
        _p("Jack Hendry", "CB", "Al-Ettifaq", 31, 35, 3, 2, 6.0, yc=4),
        _p("Scott McKenna", "CB", "Dinamo Zagreb", 29, 40, 1, 2, 6.5, yc=5),
        _p("John Souttar", "CB", "Rangers", 29, 15, 1, 3, 6.0, yc=3),
        _p("Dominic Hyam", "CB", "Wrexham", 30, 10, 0, 3, 5.5),
        _p("Scott McTominay", "CM", "Napoli", 29, 60, 12, 1, 8.5, True, yc=5),
        _p("Billy Gilmour", "CM", "Napoli", 25, 35, 2, 1, 7.5, star=True, yc=4),
        _p("John McGinn", "CM", "Aston Villa", 31, 70, 18, 1, 8.0, True, yc=6),
        _p("Lewis Ferguson", "CM", "Bologna", 26, 20, 3, 2, 7.5, yc=4),
        _p("Ryan Christie", "AM", "Bournemouth", 31, 50, 8, 2, 7.0, yc=3),
        _p("Kenny McLean", "CM", "Norwich City", 34, 45, 5, 3, 6.5),
        _p("Ben Gannon-Doak", "AM", "Bournemouth", 22, 8, 1, 3, 6.5),
        _p("Findlay Curtis", "CM", "Kilmarnock", 19, 2, 0, 3, 6.0),
        _p("Che Adams", "ST", "Torino", 29, 35, 10, 1, 7.0, yc=2),
        _p("Lyndon Dykes", "ST", "Charlton Athletic", 30, 40, 12, 2, 6.5, yc=3),
        _p("Ross Stewart", "ST", "Southampton", 29, 5, 1, 2, 6.5),
        _p("Lawrence Shankland", "ST", "Hearts", 30, 20, 5, 3, 6.0),
        _p("George Hirst", "ST", "Ipswich Town", 27, 10, 2, 3, 6.0),
    ])


def switzerland_squad() -> Squad:
    return Squad(team_name="瑞士", group="B", coach="Murat Yakin", players=[
        _p("Gregor Kobel", "GK", "Borussia Dortmund", 28, 15, 0, 1, 8.5, True),
        _p("Yvon Mvogo", "GK", "Lorient", 32, 10, 0, 2, 6.5),
        _p("Marvin Keller", "GK", "Young Boys", 23, 2, 0, 3, 6.0),
        _p("Manuel Akanji", "CB", "Inter Milan", 30, 70, 4, 1, 8.0, True, yc=4),
        _p("Nico Elvedi", "CB", "Gladbach", 29, 55, 3, 1, 7.5, yc=4),
        _p("Ricardo Rodriguez", "LB", "Real Betis", 33, 120, 9, 2, 7.0, star=True, yc=3),
        _p("Silvan Widmer", "RB", "Mainz", 33, 50, 3, 2, 7.0, yc=4),
        _p("Miro Muheim", "LB", "Hamburg", 27, 10, 0, 3, 6.5),
        _p("Aurèle Amenda", "CB", "Eintracht Frankfurt", 22, 8, 0, 3, 6.5),
        _p("Eray Cömert", "CB", "Valencia", 28, 20, 1, 3, 6.0, yc=5),
        _p("Luca Jaquez", "CB", "VfB Stuttgart", 22, 5, 0, 3, 6.5),
        _p("Granit Xhaka", "CM", "Sunderland", 33, 135, 15, 1, 8.0, True, yc=7),
        _p("Remo Freuler", "CM", "Bologna", 34, 80, 8, 2, 7.0, yc=5),
        _p("Denis Zakaria", "DM", "Monaco", 29, 55, 4, 2, 7.5, yc=5),
        _p("Ardon Jashari", "CM", "AC Milan", 23, 15, 1, 2, 7.0, yc=3),
        _p("Djibril Sow", "CM", "Sevilla", 28, 45, 3, 2, 7.0, yc=4),
        _p("Christian Fassnacht", "AM", "Young Boys", 32, 20, 4, 3, 6.5),
        _p("Michel Aebischer", "CM", "Pisa", 29, 25, 1, 3, 6.5),
        _p("Fabian Rieder", "AM", "Augsburg", 24, 15, 2, 3, 6.5),
        _p("Johan Manzambi", "CM", "Freiburg", 22, 5, 0, 3, 6.0),
        _p("Rubén Vargas", "AM", "Sevilla", 27, 30, 5, 3, 6.5),
        _p("Breel Embolo", "ST", "Rennes", 29, 70, 15, 1, 7.5, star=True, yc=2),
        _p("Noah Okafor", "LW", "Leeds United", 26, 25, 5, 2, 7.0, yc=2),
        _p("Dan Ndoye", "RW", "Nottingham Forest", 25, 20, 3, 2, 7.0),
        _p("Zeki Amdouni", "ST", "Burnley", 25, 15, 5, 3, 6.5),
        _p("Cedric Itten", "ST", "Fortuna Düsseldorf", 29, 10, 3, 3, 6.0),
    ])


def bosnia_squad() -> Squad:
    return Squad(team_name="波黑", group="B", coach="Sergej Barbarez", players=[
        _p("Nikola Vasilj", "GK", "FC St. Pauli", 30, 10, 0, 1, 6.5),
        _p("Martin Zlomislić", "GK", "HNK Rijeka", 28, 5, 0, 2, 6.0),
        _p("Osman Hadžikić", "GK", "Slaven Belupo", 29, 2, 0, 3, 5.5),
        _p("Sead Kolašinac", "LB", "Atalanta", 33, 60, 2, 1, 7.0, star=True, yc=6),
        _p("Amar Dedić", "RB", "Benfica", 23, 15, 1, 1, 7.0, star=True, yc=3),
        _p("Nihad Mujakić", "CB", "Gaziantep FK", 27, 20, 1, 2, 6.5, yc=5),
        _p("Nikola Katić", "CB", "Schalke 04", 29, 15, 1, 2, 6.5, yc=5),
        _p("Tarik Muharemović", "CB", "Sassuolo", 23, 8, 0, 2, 6.5, yc=4),
        _p("Stjepan Radeljić", "CB", "HNK Rijeka", 28, 10, 0, 3, 6.0),
        _p("Dennis Hadžikadunić", "CB", "Sampdoria", 27, 15, 0, 3, 6.0, yc=4),
        _p("Nidal Čelik", "LB", "Lens", 24, 5, 0, 3, 6.5),
        _p("Amir Hadžiahmetović", "CM", "Hull City", 29, 30, 2, 1, 6.5, yc=5),
        _p("Ivan Šunjić", "DM", "Pafos FC", 29, 35, 1, 2, 6.5, yc=6),
        _p("Ivan Bašić", "CM", "FC Astana", 24, 10, 1, 3, 6.0),
        _p("Dženis Burnić", "CM", "Karlsruher SC", 28, 15, 1, 3, 6.0, yc=4),
        _p("Ermin Mahmić", "CM", "Slovan Liberec", 26, 8, 0, 3, 5.5),
        _p("Benjamin Tahirović", "CM", "Brøndby IF", 23, 12, 1, 2, 6.5),
        _p("Amar Memić", "AM", "Viktoria Plzeň", 24, 5, 0, 3, 6.0),
        _p("Armin Gigović", "CM", "Young Boys", 24, 10, 0, 2, 6.5),
        _p("Kerim Alajbegović", "AM", "RB Salzburg", 25, 8, 1, 3, 6.5),
        _p("Esmir Bajraktarević", "RW", "PSV Eindhoven", 21, 5, 1, 2, 7.0, star=True),
        _p("Edin Džeko", "ST", "Schalke 04", 40, 140, 73, 1, 7.5, True, yc=2),
        _p("Ermedin Demirović", "ST", "VfB Stuttgart", 28, 25, 8, 1, 7.5, yc=3),
        _p("Haris Tabaković", "ST", "Borussia Mönchengladbach", 31, 15, 5, 2, 6.5),
        _p("Samed Baždar", "ST", "Jagiellonia Białystok", 22, 5, 1, 3, 6.0),
        _p("Jovo Lukić", "ST", "Universitatea Cluj", 26, 3, 0, 3, 5.5),
    ])


def all_seed_squads() -> list[Squad]:
    return [brazil_squad(), scotland_squad(), switzerland_squad(), bosnia_squad()]

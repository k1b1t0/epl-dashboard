import hashlib
import plotly.express as px

# Preset fallback colors for famous EPL clubs if desired, but dynamic hashing ensures any team gets a stable color!
FAMOUS_TEAM_COLORS = {
    "Arsenal FC": "#EF0107",
    "Chelsea FC": "#034694",
    "Liverpool FC": "#C8102E",
    "Manchester City FC": "#6CABDD",
    "Manchester United FC": "#DA291C",
    "Tottenham Hotspur FC": "#132257",
}

def generate_dynamic_team_color(team_name: str) -> str:
    """Generates a stable, consistent color HEX code for any team name dynamically using MD5 hashing.
    No hardcoding required; adding/removing teams automatically maintains color stability.
    """
    if team_name in FAMOUS_TEAM_COLORS:
        return FAMOUS_TEAM_COLORS[team_name]
    
    # Hash team name to pick a stable color from Plotly's extended color palette
    palette = px.colors.qualitative.Dark24 + px.colors.qualitative.Alphabet
    hash_digest = hashlib.md5(team_name.encode('utf-8')).hexdigest()
    color_index = int(hash_digest, 16) % len(palette)
    return palette[color_index]

def get_team_color_map(team_names: list) -> dict:
    """Returns a dictionary mapping each team to its stable color."""
    return {team: generate_dynamic_team_color(team) for team in team_names}

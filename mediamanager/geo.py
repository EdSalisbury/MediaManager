from geopy.geocoders import Nominatim
import logging
from ratelimit import limits, sleep_and_retry

logger = logging.getLogger("mediamanager")

def get_coords(exif_data):
    if not exif_data:
        return None

    gps_tag_id = 34853
    if gps_tag_id not in exif_data:
        return None

    north = exif_data.get(gps_tag_id, {}).get(2, ())
    east = exif_data.get(gps_tag_id, {}).get(4, ())
    if not north or not east:
        return None

    lat = float(((((north[0] * 60) + north[1]) * 60) + north[2]) / 60 / 60)
    long = float(((((east[0] * 60) + east[1]) * 60) + east[2]) / 60 / 60)
    if exif_data.get(gps_tag_id, {}).get(1, "") == "S":
        lat *= -1.0
    if exif_data.get(gps_tag_id, {}).get(3, "") == "W":
        long *= -1.0
    return (lat, long)


def round_coordinates(coordinate_tuple, precision=6):
    """
    Round the coordinates in the tuple to a specified precision.

    :param coordinate_tuple: A tuple of coordinates (e.g., (x, y)).
    :param precision: Number of decimal places to round to.
    :return: A new tuple with rounded coordinates.
    """
    return tuple(round(coord, precision) for coord in coordinate_tuple)


def tuple_to_dbm_key(coordinate_tuple, precision=6):
    """
    Convert a rounded coordinate tuple to a suitable key for dbm.

    :param coordinate_tuple: A tuple of coordinates (e.g., (x, y)).
    :param precision: Number of decimal places to round to before converting to key.
    :return: Encoded byte string suitable for dbm keys.
    """
    # Round the coordinates
    rounded_tuple = round_coordinates(coordinate_tuple, precision)

    # Convert tuple to string
    tuple_str = str(rounded_tuple)

    # Encode the string to bytes
    key_bytes = tuple_str.encode('utf-8')

    return key_bytes


@sleep_and_retry
@limits(calls=1, period=5)
def get_location(coords):
    logger.info(f"Getting location for {coords}")
    try:
        geo = Nominatim(user_agent="MediaManager")
        loc = geo.reverse(f"{coords[0]},{coords[1]}")
        return loc.raw.get("address", {})
    except Exception:
        return dict()


def get_address(db, cfg, coords):
    if not coords:
        return None

    coords = round_coordinates(coords)
    key = tuple_to_dbm_key(coords)
    address = db.load_value(key)

    if not address:
        address = dict()
        try:
            address = get_location(coords)
            db.save_value(key, address)
        except Exception:
            pass

    house_number = address.get("house_number")
    road = address.get("road")
    city = address.get("city")
    if not city:
        city = address.get("town")
    if not city:
        city = address.get("county")

    state = address.get("ISO3166-2-lvl4", "")
    if state.startswith("US-"):
        state = state[3:]
    lookup = f"{house_number} {road}, {city}, {state}"
    if lookup in cfg.get("locations"):
        return cfg.get("locations").get(lookup)
    if road:
        return (f"{road}, {city}, {state}")
    return (f"{city}, {state}")

import os
import random
import urllib
from datetime import datetime

# FTS / Geo spatial queries
import couchbase.search as search

import flickrapi
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Couchbase cluster operations
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.exceptions import CouchbaseException

# Country metadata
from countryinfo import CountryInfo
from dotenv import load_dotenv

COUNTRIES = [
    "Afghanistan",
    "Åland Islands",
    "Albania",
    "Algeria",
    "American Samoa",
    "Andorra",
    "Angola",
    "Anguilla",
    "Antarctica",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Aruba",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Bouvet Island",
    "Brazil",
    "British Indian Ocean Territory",
    "Brunei Darussalam",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Cayman Islands",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Christmas Island",
    "Cocos (Keeling) Islands",
    "Colombia",
    "Comoros",
    "Congo",
    "Congo, The Democratic Republic of The",
    "Cook Islands",
    "Costa Rica",
    "Cote D'ivoire",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Ethiopia",
    "Falkland Islands (Malvinas)",
    "Faroe Islands",
    "Fiji",
    "Finland",
    "France",
    "French Guiana",
    "French Polynesia",
    "French Southern Territories",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Gibraltar",
    "Greece",
    "Greenland",
    "Grenada",
    "Guadeloupe",
    "Guam",
    "Guatemala",
    "Guernsey",
    "Guinea",
    "Guinea-bissau",
    "Guyana",
    "Haiti",
    "Heard Island and Mcdonald Islands",
    "Holy See (Vatican City State)",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran, Islamic Republic of",
    "Iraq",
    "Ireland",
    "Isle of Man",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jersey",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea, Democratic People's Republic of",
    "Korea, Republic of",
    "Kuwait",
    "Kyrgyzstan",
    "Lao People's Democratic Republic",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libyan Arab Jamahiriya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Macao",
    "Macedonia, The Former Yugoslav Republic of",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Martinique",
    "Mauritania",
    "Mauritius",
    "Mayotte",
    "Mexico",
    "Micronesia, Federated States of",
    "Moldova, Republic of",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Montserrat",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "Netherlands Antilles",
    "New Caledonia",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "Niue",
    "Norfolk Island",
    "Northern Mariana Islands",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestinian Territory, Occupied",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Pitcairn",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Reunion",
    "Romania",
    "Russian Federation",
    "Rwanda",
    "Saint Helena",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Pierre and Miquelon",
    "Saint Vincent and The Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Georgia and The South Sandwich Islands",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Svalbard and Jan Mayen",
    "Swaziland",
    "Sweden",
    "Switzerland",
    "Syrian Arab Republic",
    "Taiwan, Province of China",
    "Tajikistan",
    "Tanzania, United Republic of",
    "Thailand",
    "Timor-leste",
    "Togo",
    "Tokelau",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Turks and Caicos Islands",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "United States Minor Outlying Islands",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Viet Nam",
    "Virgin Islands, British",
    "Virgin Islands, U.S.",
    "Wallis and Futuna",
    "Western Sahara",
    "Yemen",
    "Zambia",
    "Zimbabwe",
]

load_dotenv()

# set app layout
st.set_page_config(
    page_title="Travel Exploration",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    """Download a single file and make its content available as a string"""
    url = (
        "https://raw.githubusercontent.com/nithishr/visualize-location-history/main/"
        + path
    )
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


def get_pics_from_location(locations_df, size=10):
    """Get images from flickr using the gps coordinates"""
    api_key = os.getenv("FLICKR_API_KEY")
    api_secret = os.getenv("FLICKR_API_SECRET")
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format="parsed-json")
    urls = set()

    for index, row in locations_df.iterrows():
        try:
            photos = flickr.photos.search(
                lat=row["latitude"], lon=row["longitude"], per_page=10, pages=1
            )
            # Get a random image from the set of images
            choice_max = min(size - 1, int(photos["photos"]["total"]))
            selection = random.randint(0, choice_max)
            selected_photo = photos["photos"]["photo"][selection]

            # Compute the url for the image
            url = f"https://live.staticflickr.com/{selected_photo['server']}/{selected_photo['id']}_{selected_photo['secret']}_w.jpg"
            urls.add(url)
        except Exception as e:
            print(e)
            continue
    return list(urls)


def query_country_polygon(cluster, polygon):
    """Method to search for locations within a polygon"""
    res = cluster.search_query(
        "gps_index",
        search.GeoPolygonQuery(polygon_points=polygon, field="geo"),
        search.SearchOptions(limit=800000, fields=["ts", "geo"]),
    )

    return res


def query_radius(cluster, point, radius):
    """Method to search for locations within a search radius around a point (longitude, latitude)"""
    res = cluster.search_query(
        "gps_index",
        search.GeoDistanceQuery(distance=radius, location=point, field="geo"),
        search.SearchOptions(limit=100000, fields=["ts", "geo"], sort=["geo_distance"]),
    )
    return res


def get_cities(cluster):
    """Query to get all the cities stored in the database"""
    cities = None
    try:
        result = cluster.query("select city_ascii from `location-data`._default.cities")
        cities = [row["city_ascii"] for row in result]
    except CouchbaseException as ex:
        st.warning("Error connecting to the Database")
        print(ex)
    return cities


def get_city_coordinates(cluster, city):
    """Query to get the GPS coordinates for a single city in the database"""
    point = []
    try:
        result = cluster.query(
            "select lat, lng from `location-data`._default.cities where city_ascii=$city",
            city=city,
        )
        for res in result:
            point = [res["lng"], res["lat"]]
    except CouchbaseException as ex:
        st.warning("Error connecting to the Database")
        print(ex)
    return point


# get a reference to our cluster
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
cluster = Cluster(
    f"couchbase://{DB_HOST}",
    ClusterOptions(PasswordAuthenticator(DB_USER, DB_PASSWORD)),
)

# get a reference to our bucket
cb = cluster.bucket("location-data")

# Application Inputs
st.sidebar.subheader("Inputs")
choice = st.sidebar.selectbox(label="Demo", options=["Select", "Cities", "Countries"])

# Countries Demo
if choice == "Countries":
    country = st.sidebar.selectbox(label="Country", options=COUNTRIES)

    try:
        # Get country information
        country_info = CountryInfo(country)
        country_details = country_info.geo_json()
        country_polygon = []
        if country_details["features"][0]["geometry"]["type"] == "MultiPolygon":
            st.warning("Incpmpatible Data")
            country_polygon = []
        else:
            country_polygon = country_details["features"][0]["geometry"]["coordinates"][
                0
            ]
    except KeyError:
        st.warning("Data not found, Try another country")
    else:
        if len(country_polygon) > 1:
            res = query_country_polygon(cluster, country_polygon)
            results = []

            # Create a Dataframe from the results to plot the map
            for row in res.rows():
                # print(row)
                res_row = {}
                res_row["longitude"] = row.fields["geo"][0]
                res_row["latitude"] = row.fields["geo"][1]
                res_row["ts"] = row.fields["ts"]
                results.append(res_row)

            travel_data = pd.DataFrame(results)

            # Map with Selected Points
            st.header("Trail Map")
            st.map(data=travel_data)
            st.caption(f"Data Points: {len(results)}")

        # Embed Wikipedia Article for more info
        st.header("Country Info")
        components.iframe(country_info.wiki(), height=450, scrolling=True)

# Cities Demo
elif choice == "Cities":
    # Get available Cities & insert it into choices
    CITIES = get_cities(cluster)

    city = st.sidebar.selectbox(label="Choose City", options=CITIES)
    search_radius = st.sidebar.selectbox(
        label="Search Radius",
        options=["500m", "5km", "10km", "15km", "25km", "50km"],
        index=2,
    )

    # Get the center coordinates of the City
    city_center = get_city_coordinates(cluster, city)
    # print(city_center)

    # Get the locations satisfying the search radius from the city's coordinates
    res = query_radius(cluster, point=city_center, radius=search_radius)

    results = []
    for row in res.rows():
        # print(row)
        res_row = {}
        res_row["longitude"] = row.fields["geo"][0]
        res_row["latitude"] = row.fields["geo"][1]
        res_row["ts"] = row.fields["ts"]
        results.append(res_row)

    travel_data = pd.DataFrame(results)

    # Map with Selected Points
    st.header("Trail Map")
    st.map(data=travel_data)
    st.caption(f"Data Points: {len(results)}")

if choice != "Select":
    show_images = st.sidebar.checkbox("Show Images")
    images_count = st.sidebar.number_input("Images to Show", value=5)
    if show_images and not travel_data.empty:
        # Show the images from Flickr's public images
        st.header("Image Highlights")
        sample_data = travel_data.sample(n=images_count)
        urls = get_pics_from_location(sample_data, images_count)
        st.image(urls, width=400)

show_code = st.sidebar.checkbox("Show Code")
if show_code:
    st.code(get_file_content_as_string("loc_viz.py"))

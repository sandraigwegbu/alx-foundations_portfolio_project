from flask import Flask, redirect, url_for, render_template, request, session
from datetime import datetime, date, time, timedelta
import requests
from math import fmod, sin, cos, asin, acos, tan, atan2, pi, degrees, radians, pow, sqrt
from os import getenv


GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
SECRET_KEY = getenv("SECRET_KEY")

app = Flask(__name__)
app.secret_key = (SECRET_KEY)
app.permanent_session_lifetime = timedelta(minutes=5)
app.url_map.strict_slashes = False


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    """index page"""
    return render_template("index.html")
    pass


@app.route("/calculator.html", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # todo: check input complete and correct before processing     #resume
        # print("POST______")
        # session.permanent = True
        city = request.form["city"]
        panelSlope = request.form["panelSlope"]
        panelAzimuth = request.form["panelAzimuth"]
        dateString = request.form["dateString"]
        rawTimeString = request.form["timeString"]
        timeString = cleanTimeString(rawTimeString)
        # timeZoneInfo = request.form["timeZoneInfo"]
        session["city"] = city
        session["panelSlope"] = panelSlope
        session["panelAzimuth"] = panelAzimuth
        session["dateString"] = dateString
        session["timeString"] = timeString

        (latitude, longitude) = latlng(city)  # debug
        if latitude is None or longitude is None:
            session["city"] = "Unknown location: {}".format(session["city"])
            initSession(session)
            return render_template("solargeometry_form_and_session.html",
                                   city=session.get("city"), panelSlope=session.get("panelSlope"),
                                   panelAzimuth=session.get("panelAzimuth"), dateString=session.get("dateString"),
                                   timeString=session.get("timeString"))

        tz_json = timeZone(latitude, longitude, dateString,
                           timeString)  # resume
        # tz = tz_json["rawOffset"]/3600
        # print("TZ JSON: ", tz_json)  # debug

        try:
            tz = (tz_json["rawOffset"] + tz_json["dstOffset"]) / \
                3600  # corrected for dst
        except KeyError:  # eg for Kazakhstan!!!
            session["city"] = "Unknown location: {}".format(session["city"])
            initSession(session)
            return render_template("solargeometry_form_and_session.html",
                                   city=session.get("city"), panelSlope=session.get("panelSlope"),
                                   panelAzimuth=session.get("panelAzimuth"), dateString=session.get("dateString"),
                                   timeString=session.get("timeString"))

        timeZoneId = tz_json["timeZoneId"]
        timeZoneName = tz_json["timeZoneName"]
        timeZoneInfo = (f"UTC+{tz}: {timeZoneId}") if (tz >
                                                       0) else (f"UTC{tz}: {timeZoneId}")
        timeZoneInfo = (f"UTC: {timeZoneId}") if (tz == 0) else (timeZoneInfo)
        # timeZoneInfo = timeZoneName
        session["timeZoneInfo"] = timeZoneInfo
        session["lat"] = latitude
        session["lng"] = longitude

        # call NOAA spreadsheet to compute key results
        (sunAzimuth, sunElevation, sunHours, sunrise, solarNoon, sunset) = noaa(
            latitude, longitude, dateString, timeString)

        # store NOAA results in session
        session["sunAzimuth"] = sunAzimuth
        session["sunElevation"] = sunElevation
        session["sunHours"] = sunHours
        session["sunrise"] = sunrise
        session["solarNoon"] = solarNoon
        session["sunset"] = sunset

        # determine cosPhi - panelSunZenithCosine
        cosPhi = panelSunZenithCosine(
            panelAzimuth, panelSlope, sunAzimuth, sunElevation)
        # solarGeo = ("%0.2f" % round(cosPhi, 2)) if (round(cosPhi, 3) > 0 and sunElevation > 0) \
        #    else ("#NA (panel in shadow)")
        solarGeo = ("%0.2f" % round(cosPhi, 2))

        # print("solarGeo: ", solarGeo)
        # print("\nLatitude: {}\n Longitude: {}".format(latitude, longitude))
        return render_template("solargeometry_form_and_session.html",
                               solarGeo=solarGeo, city=city, panelSlope=panelSlope,
                               panelAzimuth=panelAzimuth, dateString=dateString, timeString=timeString,
                               timeZoneInfo=timeZoneInfo, timeZoneName=timeZoneName, lat=round(
                                   latitude, 6),
                               lng=round(longitude, 6), sunAzimuth=("%0.1f" % round(sunAzimuth, 1)), sunElevation=("%0.1f" % round(sunElevation, 1)),
                               sunHours=round(sunHours, 2), sunrise=f"{sunrise}", solarNoon=f"{solarNoon}", sunset=f"{sunset}")

    initSession(session)

    # if "city" in session: (still necessary?)
    return render_template("solargeometry_form_and_session.html",
                           city=session.get("city"), panelSlope=session.get("panelSlope"),
                           panelAzimuth=session.get("panelAzimuth"), dateString=session.get("dateString"),
                           timeString=session.get("timeString"))
    # return render_template("solargeometry_form_and_session.html")


def initSession(session):
    print("SESSION:", session)  # debug - what is in it?

    if session.get("panelSlope") is None:
        print("Empty string for panel slope")
        session["panelSlope"] = 0
    else:
        print("Not empty slope")

    if session.get("panelAzimuth") is None:
        print("Empty string for panel direction")
        session["panelAzimuth"] = 0
    else:
        print("Not empty direction")

    if session.get("dateString") is None:
        session["dateString"] = datetime.today().strftime("%Y-%m-%d")

    if session.get("timeString") is None:
        session["timeString"] = datetime.today().strftime("%H:%M")
    return


def latlng(city):
    """Use Google geocoding API to lookup lat/lng data for city"""
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
        city + "&key=" + GOOGLE_API_KEY
    response = requests.get(url)
    try:
        location = response.json()["results"][0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
    except IndexError as e:
        latitude = None
        longitude = None
    return (latitude, longitude)


def timeZone(lat, lng, dateString, timeString):
    """ get timezone json dictionary from google timezone api based on latitude and longitude
    and a given date and time. The date and time are used to compute the timestamp parameter"""
    # timeStamp = datetime.fromisoformat(isoDate(dateString) + "T" + timeString).timestamp()
    timeStamp = datetime.fromisoformat(
        dateString + "T" + timeString).timestamp()
    # cutoff at 1.1.1970 midnight UNIX time date epoch
    timeStamp = timeStamp if (timeStamp > 0) else 0
    url = "https://maps.googleapis.com/maps/api/timezone/json?" + \
        "location=" + str(lat) + "%2C" + str(lng) + "&timestamp=" + \
        str(timeStamp) + "&key=" + GOOGLE_API_KEY
    tz_json = requests.get(url).json()
    # dstOffset = tz_json["dstOffset"]
    # rawOffset = tz_json["rawOffset"]
    # status = tz_json["status"]
    # timeZoneId = tz_json["timeZoneId"]
    # timeZoneName = tz_json["timeZoneName"]
    # print("DST Offset: ", "UTC" + str(tz_json["dstOffset"]/3600))
    return tz_json


def isoDate(dateString):
    """ convert date dd/mm/yyyy to yyyy-mm-dd"""
    splitDate = dateString.rsplit('/')
    # return f"{splitDate[2]}-{splitDate[1]}-{splitDate[0]}"
    # pad single digit dd or mm with zero; future: qc yy instead of yyyy input
    # print("dateString: ", dateString, "split: ", splitDate)
    return "%04d-%02d-%02d" % (int(splitDate[2]), int(splitDate[1]),
                               int(splitDate[0]))


def fracDaytoTime(fracDay, seconds=True):
    """Given a fractional day, eg 1.45 or 2.76 day, return the time in hh:mm:ss format
    Do not return the seconds part if seconds==False"""
    frac = fmod(fracDay, 1)
    hours = frac * 24
    hr = int(hours)
    min = (hours * 60) % 60
    sec = (hours * 3600) % 60
    if seconds == False:
        return ("%02d:%02d" % (hr, min))
    return ("%02d:%02d:%02d" % (hr, min, sec))


def cleanTimeString(rawTimeString):
    """replace '.' with ':' in rawTimeString and ensure 2-digit format"""
    temp = rawTimeString.replace('.', ':').split(':')
    return ("%02d:%02d" % (int(temp[0]), int(temp[1])))


# compute the NOAA spreadsheet and return key output
def noaa(latitude, longitude, dateString, timeString):
    """compute the NOAA spreadsheet and return key output"""
    # first compute time zone, eg +1 or -7:
    tz_json = timeZone(latitude, longitude, dateString, timeString)
    raw_tz = tz_json["rawOffset"]
    dstOffset = tz_json["dstOffset"]
    # effective_tz = raw_tz + dst_tz
    # tz = float(timeZone(latitude, longitude, dateString, timeString)["rawOffset"])/3600.0
    tz = float(raw_tz)/3600.0
    # dt - days since 1.1.1900 (adjusted for EXcel leapyear bug)
    # dt = (datetime.strptime(dateString, '%d/%m/%Y').date() - date(1899, 12,30)).days
    dt = (datetime.strptime(dateString, '%Y-%m-%d').date() - date(1899, 12, 30)).days
    # tm - time as a decimal fraction of one day, eg 12 noon is 0.5; iso eg '10:15:21'
    # deduct Daylight saving offset; add it back when calculating wall-clock times, eg solarNoon
    tm = (time.fromisoformat(timeString).hour + time.fromisoformat(timeString).minute/60 +
          time.fromisoformat(timeString).second/3600.0 - dstOffset/3600.0) / 24.0

    julianDay = dt + 2415018.5 + tm - float(tz)/24.0
    julianCentury = (julianDay - 2451545)/36525
    geomMeanLongSun = fmod2(280.46646 + julianCentury *
                            (36000.76983 + julianCentury * 0.0003032), 360)
    # if geomMeanLongSun < 0:
    #    geomMeanLongSun += 360.0
    geomMeanAnomSun = 357.52911 + julianCentury * \
        (35999.05029 - 0.0001537 * julianCentury)
    eccentEarthOrbit = 0.016708634 - julianCentury * \
        (0.000042037 + 0.0000001267 * julianCentury)
    sunEqOfCtr = sin(radians(geomMeanAnomSun)) * (1.914602 - julianCentury * (0.004817 + 0.000014 *
                                                                              julianCentury)) + sin(radians(2 * geomMeanAnomSun)) * (0.019993 - 0.000101 * julianCentury) + \
        sin(radians(3 * geomMeanAnomSun)) * 0.000289
    sunTrueLong = geomMeanLongSun + sunEqOfCtr
    sunTrueAnom = geomMeanAnomSun + sunEqOfCtr
    sunRadVector = (1.000001018 * (1 - eccentEarthOrbit * eccentEarthOrbit)) / \
        (1 + eccentEarthOrbit * cos(radians(sunTrueAnom)))
    sunAppLong = sunTrueLong - 0.00569 - 0.00478 * \
        sin(radians(125.04 - 1934.136 * julianCentury))
    meanObliqEcliptic = 23 + (26 + ((21.448 - julianCentury * (46.815 +
                                                               julianCentury * (0.00059 - julianCentury * 0.001813)))) / 60) / 60
    obliqCorr = meanObliqEcliptic + 0.00256 * cos(radians(125.04 - 1934.136 *
                                                          julianCentury))
    sunRtAscen = degrees(atan2_excel(cos(radians(sunAppLong)), cos(
        radians(obliqCorr)) * sin(radians(sunAppLong))))
    sunDeclin = degrees(asin(sin(radians(obliqCorr))
                        * sin(radians(sunAppLong))))
    varY = tan(radians(obliqCorr / 2)) * tan(radians(obliqCorr/2))
    eqOfTime = 4 * degrees(varY * sin(2 * radians(geomMeanLongSun)) - 2 *
                           eccentEarthOrbit * sin(radians(geomMeanAnomSun)) + 4 *
                           eccentEarthOrbit * varY * sin(radians(geomMeanAnomSun)) * cos(2 *
                                                                                         radians(geomMeanLongSun)) - 0.5 * varY * varY * sin(4 *
                                                                                                                                             radians(geomMeanLongSun)) - 1.25 * eccentEarthOrbit *
                           eccentEarthOrbit * sin(2 * radians(geomMeanAnomSun)))
    haSunrise = degrees(acos(cos(radians(90.833)) / (cos(radians(latitude)) *
                                                     cos(radians(sunDeclin))) - tan(radians(latitude)) *
                             tan(radians(sunDeclin))))
    # add dstOffset / 86400.0 to report time with Daylight savings (it was
    # earlier deducted fro user input prior to calculating this spreadsheet)
    solarNoon = (720.0 - 4.0 * longitude - eqOfTime + float(tz)
                 * 60.0) / 1440.0 + dstOffset / 86400.0
    # + dstOffset / 86400.0 (double add! caused bug!)
    sunriseTime = solarNoon-haSunrise * 4 / 1440
    # + dstOffset / 86400.0 (double add! casued bug!)
    sunsetTime = solarNoon + haSunrise * 4 / 1440
    sunlightDuration = 8 * haSunrise
    trueSolarTime = fmod2(tm * 1440 + eqOfTime + 4 *
                          longitude - 60 * float(tz), 1440)
    # hourAngle = IF(trueSolarTime / 4 < 0,trueSolarTime / 4 + 180, trueSolarTime / 4 - 180)
    hourAngle = (trueSolarTime / 4 + 180) if (trueSolarTime /
                                              4 < 0) else (trueSolarTime / 4 - 180)
    solarZenithAngle = degrees(acos(sin(radians(latitude)) * sin(radians(
        sunDeclin)) + cos(radians(latitude)) * cos(radians(sunDeclin)) *
        cos(radians(hourAngle))))
    solarElevAngle = 90 - solarZenithAngle
    # approxAtmRefraction = IF(solarElevAngle > 85, 0, IF(solarElevAngle > 5, \
    #    58.1 / tan(radians(solarElevAngle)) - 0.07 / pow(tan(radians( \
    #    solarElevAngle)), 3) + 0.000086 / pow(tan(radians(solarElevAngle)), \
    #   5), IF(solarElevAngle > -0.575, 1735 + solarElevAngle * (-518.2 + \
    #    solarElevAngle * (103.4 + solarElevAngle * (-12.79 + solarElevAngle * \
    #    0.711))), -20.772 / tan(radians(solarElevAngle))))) / 3600

    approxAtmRefraction = ((0) if (solarElevAngle > 85) else (
        (58.1 / tan(radians(solarElevAngle)) - 0.07 / pow(tan(radians(
            solarElevAngle)), 3) + 0.000086 / pow(tan(radians(solarElevAngle)),
                                                  5)) if (solarElevAngle > 5) else (
            (1735 + solarElevAngle * (-518.2 +
                                      solarElevAngle * (103.4 + solarElevAngle * (-12.79 + solarElevAngle *
                                                        0.711)))) if (solarElevAngle > -0.575) else (-20.772 / tan(radians(solarElevAngle)))
        )
    )) / 3600

    solarElevCorrForAtmRefraction = solarElevAngle + approxAtmRefraction

    # solarAzimuthAngle = IF(hourAngle > 0, fmod(degrees(acos(((sin(radians( \
    #    latitude)) * cos(radians(solarZenithAngle))) - sin(radians( \
    #    sunDeclin))) / (cos(radians(latitude)) * sin(radians( \
    #    solarZenithAngle))))) + 180, 360), fmod(540 - degrees(acos((( \
    #    sin(radians(latitude)) * cos(radians(solarZenithAngle))) - sin( \
    #    radians(sunDeclin))) / (cos(radians(latitude)) * sin(radians( \
    #    solarZenithAngle))))), 360))

    solarAzimuthAngle = (fmod2(degrees(acos(((sin(radians(
        latitude)) * cos(radians(solarZenithAngle))) - sin(radians(
            sunDeclin))) / (cos(radians(latitude)) * sin(radians(
                solarZenithAngle))))) + 180, 360)) if (hourAngle > 0) else (
        fmod2(540 - degrees(acos(((
            sin(radians(latitude)) * cos(radians(solarZenithAngle))) - sin(
            radians(sunDeclin))) / (cos(radians(latitude)) * sin(radians(
                solarZenithAngle))))), 360))

    print(latitude, longitude, tz, dateString, timeString)
    print(dt, tm, julianDay, julianCentury, geomMeanLongSun,
          geomMeanAnomSun, eccentEarthOrbit, sunEqOfCtr)
    print(sunTrueLong, sunTrueAnom, sunRadVector, sunAppLong, meanObliqEcliptic)
    print(obliqCorr, sunRtAscen, sunDeclin, varY, eqOfTime)
    print(haSunrise, fracDaytoTime(solarNoon), fracDaytoTime(
        sunriseTime), fracDaytoTime(sunsetTime))
    print(solarNoon, sunriseTime, sunsetTime)
    print(sunlightDuration, trueSolarTime, hourAngle)
    print(solarZenithAngle, solarElevAngle, approxAtmRefraction,
          solarElevCorrForAtmRefraction, solarAzimuthAngle)
    # (170.3, 45.1, 5.2, '12:08')
    return (solarAzimuthAngle, solarElevAngle, sunlightDuration / 60, fracDaytoTime(
        sunriseTime, seconds=False), fracDaytoTime(solarNoon, seconds=False),
        fracDaytoTime(sunsetTime, seconds=False))


def fmod2(a, b):
    fm = fmod(a, b)
    return (fm if (fm > 0) else (fm + b))


def atan2_excel(y, x):
    return ((pi / 2) - atan2(y, x))


def panelSunZenithCosine(panelAzimuth, panelSlope, sunAzimuth, sunElevation):
    """Return the cosine of the angle between the panel normal and the
    direction of the sun. This is by definition the dot product of the unit
    vectors in the direction of sun and panel mormal. If this is negative,
    then the panel is facing away from the sun."""
    panelPlanProjection = cos(radians(90 - int(panelSlope)))
    sunPlanProjection = cos(radians(sunElevation))
    deltaAzimuth = int(panelAzimuth) - sunAzimuth
    deltaBaseProjection = sqrt((panelPlanProjection * panelPlanProjection +
                                sunPlanProjection * sunPlanProjection - 2 * panelPlanProjection *
                                sunPlanProjection * cos(radians(deltaAzimuth))))
    # phi is the angle between panel normal and sun direction: \./
    # cosPhi = (r1^2 + r2^2 - s^2) / ( 2 * r1 * r2)   where r1, r2 and s
    # define the subtended triangle between panel normal and sun.
    # r1 = r2 = 1:
    deltaVertProjection = sin(
        radians(90 - int(panelSlope))) - sin(radians(sunElevation))
    panelSunVector = sqrt(deltaBaseProjection * deltaBaseProjection +
                          deltaVertProjection * deltaVertProjection)
    cosPhi = (2.0 - panelSunVector * panelSunVector) / 2.0
    print("panelPlanProjection: ", panelPlanProjection)
    print("sunPlanProjection: ", sunPlanProjection)
    print("deltaAzimuth: ", deltaAzimuth)
    print("deltaBaseProjection: ", deltaBaseProjection)
    print("deltaVertProjection: ", deltaVertProjection)
    print("panelSunVector: ", panelSunVector)
    print("cosPhi: ", cosPhi)
    return cosPhi


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

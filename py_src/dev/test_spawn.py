from simcore import TargetManager

if __name__ == "__main__":
    tm = TargetManager()
    # taken from test.gpx of club field east I think? I forgor alr
    dropzone_gps_boundary = [
        (33.643331523205276, -117.82649921958408),
        (33.64309980466308, -117.82603632940095),
        (33.64298166475855, -117.82580032842527),
        (33.64258775883557, -117.82606082978862),
        (33.6424739872011, -117.82613607025635),
        (33.642686047747716, -117.82661235996841),
        (33.64279532652712, -117.82685780099555),
        (33.64279532652712, -117.82685780099555),
        (33.64318820293875, -117.82659506498103),
        (33.643331523205276, -117.82649921958408),
    ]
    # Center of the dropzone above
    home_lat = 33.642947
    home_lon = -117.826344
    while True:
        try:
            tm.respawn_targets(dropzone_gps_boundary, home_lat, home_lon)
            input("Press Enter to respawn targets...")
        except KeyboardInterrupt:
            tm.delete_all_targets()
            print("Exiting...")
            break

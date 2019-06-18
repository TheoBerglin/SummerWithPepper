from APIConnections.VasttrafikAPI import VasttrafikClient


def clean_close_stops(close_stops):
    """
    Methods that removes duplicate close stops. That is the different sections of each stop.
    :param close_stops: Close stops data from API
    :return: cleaned close stops data
    """
    cleaned = list()
    found_stations = list()
    for stop in close_stops:
        if stop['name'] not in found_stations:
            cleaned.append(stop)
            found_stations.append(stop['name'])
    return cleaned


class Vasttrafik:
    
    def __init__(self, lat=57.705824, long=11.940407):
        """
        Constructor for the Vasttrafik class
        :param lat: Latitude location of Pepper, default Ericsson Lindholmen
        :param long: Longitude location of Pepper, default Ericsson Lindholmen
        """
        self.lat = lat
        self.long = long
        self.client = VasttrafikClient()

    def show_next_departure(self, stop_name=None):
        """
        Should display the next departures given Peppers location.
        :param stop_name: Check next ride for this stop. Default None
        :return:
        """
        departure_data = self.extract_next_departure(stop_name)
        self.display_next_ride(departure_data)  # Display the extracted data

    def extract_next_departure(self, stop_name=None):
        """
        Extract the next departure from a stop or a coordinate
        :param stop_name: Name of the stop, default is None
        :return: dict of departure data departure_data['Station_name'] = API_data
        """
        departure_data = dict()
        if stop_name is not None:
            try:
                stop_ids = self.client.get_stops_by_name(stop_name)
                departure_data[stop_name] = self.client.get_departures(stop_ids[0]['id'])
            except Exception as e:
                print e
        else:
            close_stops = self.client.get_nearby_stops(self.lat, self.long)  # get_close_stops
            close_stops = clean_close_stops(close_stops)  # Remove duplicates
            for stop in close_stops:  # Get all close stop departures
                departure_data[stop['name']] = self.client.get_departures(stop['id'])  # get_departures from close_stops
        return departure_data

    def plan_a_trip(self):
        """
        Method for planning a trip.
        Should initiate dialog, retrieve start and stop and calculate trip
        :return:
        """
        pass

    def display_a_trip(self, data):
        """
        Should display a trip. Either via speech, tablet or both
        :param data: The data needed for displaying a trip
        :return:
        """
        pass

    def display_next_ride(self, data):
        """
        Should display the next rides. Either via speech, tablet or both
        :param data: The data needed for displaying the next rides
        :return:
        """
        pass


if __name__ == '__main__':
    v = Vasttrafik()
    v.show_next_departure('Brunnsparken')
    print 'for debug'

from APIConnections.VasttrafikAPI import VasttrafikClient
import datetime


class Vasttrafik:
    
    def __init__(self, lat=57.705824, long=11.940407):
        """
        Constructor for the Vasttrafik class
        :param lat: Latitude location of Pepper, default Ericsson Lindholmen
        :param long: Longitude location of Pepper, default Ericsson Lindholmen
        """
        self.lat = lat
        self.long = long
        # Client
        self.client = VasttrafikClient()
        # Fields for data handling
        self.next_departure = None
        self.time_extracted = None
        self.trip = None

    def extract_next_departure(self, stop_name=None):
        """
        Extract the next departure from a stop or a coordinate
        :param stop_name: Name of the stop, default is None
        :return: dict of departure data departure_data['Station_name'] = API_data
        """
        departure_data = dict()
        # If we are given a stop, use it. Else, based on location
        if stop_name is not None:
            try:
                stop_ids = self.client.get_stops_by_name(stop_name)
                departure_data[stop_name] = self.client.get_departures(stop_ids[0]['id'])
            except Exception as e:
                print e
        else:
            close_stops = self.client.get_nearby_stops(self.lat, self.long)  # get_close_stops
            close_stops = self.remove_duplicate_stops(close_stops)  # Remove duplicates
            for stop in close_stops:  # Get all close stop departures
                departure_data[stop['name']] = self.client.get_departures(stop['id'])  # get_departures from close_stops
        self.next_departure = departure_data
        self.set_extracted_time()

    def calculate_trip(self, start_station='Lindholmen', stop_station='Prinsgatan'):
        """
        Method for calculating a trip.
        Should calculate trip from a given station to another
        :param start_station: Station for which the trip should start from. Default Lindholmen
        :param stop_station: End station of the trip. Default Prinsgatan
        :return:
        """
        pass

    def get_trip(self):
        """
        :return: Latest calculated trip
        """
        return self.trip

    def get_next_departure(self):
        """
        :return: Latest extracted departures
        """
        return self.next_departure

    def get_extracted_time(self):
        """
        :return: Time for latest extracted departure data
        """
        return self.time_extracted

    def set_extracted_time(self, time=datetime.datetime.now()):
        """
        :param time: Time when next departure data was extracted. Default is now.
        :return:
        """
        self.time_extracted = time

    @staticmethod
    def remove_duplicate_stops(close_stops):
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


if __name__ == '__main__':
    v = Vasttrafik()
    v.extract_next_departure('Brunnsparken')
    print ' for debug'

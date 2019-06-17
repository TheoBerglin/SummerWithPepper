from APIConnections.VasttrafikAPI import VasttrafikClient


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

    def show_me_the_next_ride(self, stop_id=None):
        """
        Should display the next ride given Peppers location.
        :param stop_id: Check next ride for this stop. Default None
        :return:
        """
        pass

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

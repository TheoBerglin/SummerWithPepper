# -*- coding: utf-8 -*-
import os

from APIConnections.VasttrafikAPI import VasttrafikClient
import datetime


class Vasttrafik:

    def __init__(self, save_path, lat=57.705824, long=11.940407):
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

        self.html_data = None
        self.save_path = save_path

    # Get-methods
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

    # Set-methods
    def set_extracted_time(self, time=datetime.datetime.now()):
        """
        :param time: Time when next departure data was extracted. Default is now.
        :return:
        """
        self.time_extracted = time

    # Next departure data extraction
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

    # Calculate a trip data extraction
    def calculate_trip(self, start_station='Lindholmen', end_station='Prinsgatan'):
        """
        Method for calculating a trip.
        Should calculate trip from a given station to another
        :param start_station: Station for which the trip should start from. Default Lindholmen
        :param end_station: End station of the trip. Default Prinsgatan
        :return:
        """
        start_id = self.client.get_stops_by_name(start_station)[0]['id']
        end_id = self.client.get_stops_by_name(end_station)[0]['id']
        self.trip = self.client.calculate_trip_stations(start_id, end_id)

    # Create next departure html
    def create_departure_html(self, name='departure'):
        """
        Create the next departure data html page
        :return:
        """
        if self.get_next_departure() is None:
            self.extract_next_departure()
        table_data = self.extract_departure_table_data()
        # self.next_departure = sorted(self.next_departure, key=lambda x: int(x['sname'])
        self.html_data = list()  # Remove old shit
        # Go through table data
        for station in sorted(table_data):
            departure_data = table_data[station]
            self.add_departure_header(station)  # New station, new header
            #  Go through each departure for the station
            for departure in departure_data:
                self.departure_row(departure)
            self.add_html_data('</table>')  # End current table

        # End of full code
        self.add_html_data('</body>')
        self.add_html_data('</html>')
        self.write_html_file(name)

    def extract_departure_table_data(self):
        """
        Create table data out of extracted raw departure data from the API
        :return:
        """
        self.clean_departure_data()
        tables = dict()
        # Extract 2 departures for each number+destination
        for station, station_data in self.next_departure.iteritems():
            ind = 0
            table_data = list()
            while ind < len(station_data):
                if ind == len(station_data) - 1:
                    data_dict = {'1': station_data[ind], '2': None}
                    table_data.append(data_dict)
                    ind += 1
                else:
                    if station_data[ind]['sname'] == station_data[ind + 1]['sname'] and \
                            station_data[ind]['sname'] == station_data[ind + 1]['sname'] and \
                            station_data[ind]['sname'] == station_data[ind + 1]['sname']:

                        data_dict = {'1': station_data[ind], '2': station_data[ind + 1]}
                        ind += 2
                    else:
                        data_dict = {'1': station_data[ind], '2': None}
                        ind += 1
                    table_data.append(data_dict)
            tables[station] = table_data
            # table_data[station]

        return tables

    def clean_departure_data(self):
        """
        Clean the departure data so that each combination has at maximum 2 departures.
        :return:
        """
        for station, departure_data in self.next_departure.iteritems():
            found_combinations = dict()
            new_departure_data = list()
            for dep in departure_data:
                # Add structure for combination of name+destination
                if dep['sname'] not in found_combinations:
                    found_combinations[dep['sname']] = dict()
                if dep['direction'] not in found_combinations[dep['sname']]:
                    found_combinations[dep['sname']][dep['direction']] = 0
                # Add first two occurrences of combination
                if found_combinations[dep['sname']][dep['direction']] < 2:
                    new_departure_data.append(dep)
                    found_combinations[dep['sname']][dep['direction']] += 1

            self.next_departure[station] = self.sort_departure_board(new_departure_data)

    @staticmethod
    def sort_departure_board(l):
        """
        Sort a departure board based on name, direction and time. In that order
        :param l: Departure board
        :return:
        """
        return sorted(l, key=lambda x: (int(x['sname']), x['direction'], x['time']))

    def add_departure_header(self, station='Station unknown'):
        """
        Header for a departure data table
        :param station: The departures are from this station
        :return:
        """
        self.add_html_data('<h2>%s</h2>' % station)
        self.add_html_data('<table title="Forecasts:" class="tableMenuCell" cellspacing="0" cellpadding="4" id="t01">')
        self.add_html_data('<tr class="darkblue_pane" style="color:Blue;font-weight:bold;">')
        self.add_html_data('<th align="left" scope="col">Line</th>')
        self.add_html_data('<th align="left" scope="col">Destination</th>')
        self.add_html_data('<th align="left" scope="col">Next departure</th>')
        self.add_html_data('<th align="left" scope="col">Afterwards</th>')
        self.add_html_data('</tr>')

    def departure_row(self, departure):
        """
        Creates a html row given API departure data
        :param departure: Departure data from the API
        :return:
        """
        # Extract data needed
        front_c = departure['1']['fgColor']
        back_c = departure['1']['bgColor']
        name = departure['1']['sname']
        direction = departure['1']['direction']
        if 'rtTime' in departure['1']:
            t1 = departure['1']['rtTime']
        else:
            t1 = departure['1']['time']
        t1 = self.time_to_departure(t1)

        if departure['2'] is None:
            t2 = '--'
        else:
            if 'rtTime' in departure['2']:
                t2 = departure['2']['rtTime']
            else:
                t2 = departure['2']['time']
            t2 = self.time_to_departure(t2)
        # Add html rows
        self.add_html_data('<tr>')
        self.add_html_data('<td align="center" style="color:%s;background-color:%s;">%s</td>' % (back_c, front_c, name))
        self.add_html_data('<td >%s</td>' % direction)
        self.add_html_data('<td >%s</td>' % t1)
        self.add_html_data('<td >%s</td>' % t2)
        self.add_html_data('</tr>')

    @staticmethod
    def time_to_departure(t):
        """
        Time from now to time t in minutes.
        :param t: time given as a string on format "HH:MM"
        :return: String, time from now to time t in minutes. 0 is returned as now.
        """
        now = datetime.datetime.now()
        now_str = now.strftime('%H:%M')
        diff = datetime.datetime.strptime(t, '%H:%M') - datetime.datetime.strptime(now_str, '%H:%M')
        t = int(diff.total_seconds() / 60)
        if t == 0:
            t = 'Now'
        return str(t)

    def add_html_data(self, d):
        """
        Add data to the field containing html data
        :param d: data to be appended to the field
        :return:
        """
        self.html_data.append('%s\n' % d.encode("utf-8", errors="ignore"))

    def write_html_file(self, name):
        """
        Write the data of the field html_data to a specified output file with name NAME
        :param name: name of the output html file
        :return:
        """
        with open(r'%s/%s.htm' % (self.save_path, name), 'w+') as output_file:
            # Write template

            with open(os.path.dirname(os.path.abspath(__file__)) +'\\html_template.txt', 'r') as template:
                output_file.writelines(template)
            # Write table data created by script
            for l in self.html_data:
                output_file.write(replace_swedish_html(l))


def replace_swedish_html(l):
    """
    html has different encoding than utf-8. Replace swedish letters and special letters accordingly.
    :param l: string that might contain special characters.
    :return: string ready for html
    """
    l = l.replace('ä', '&auml;').replace('ö', '&ouml;').replace('å', '&aring;')
    return l.replace('Ä', '&Auml;').replace('Ö', '&Ouml;').replace('Å', '&Aring;').replace('é', '&eacute;')


if __name__ == '__main__':
    v = Vasttrafik('C:\Users\etehreb\Documents\SummerWithPepper\Applications')
    # v.extract_next_departure()
    html_name = 'departure'
    v.create_departure_html(html_name)
    v.calculate_trip()
    #ref_id = v.trip['TripList']['Trip'][0]['Leg'][1]['JourneyDetailRef']['ref']
    #apa = v.client.get_journey_details(ref_id)
    print 'for debug'
    # sorted(apa, key=lambda x: (int(x['sname'])))

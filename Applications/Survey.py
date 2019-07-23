import matplotlib.pyplot as plt
import datetime
import json
import os

PIE_COLOR = ['#ff9999', '#99ff99', '#ffcc99']
SURVEY_FIELDS = ['good', 'neutral', 'bad']


class Survey:

    def __init__(self, save_path):
        self.survey_information = {'full_information': list(),
                                   'result': {'good': 0,
                                              'neutral': 0,
                                              'bad': 0}}
        self.save_path = save_path

    def register_click(self, button):
        reg_time = datetime.datetime.now()
        reg_time = reg_time.strftime('%d/%m/%Y, %H:%M:%S')
        self.survey_information['full_information'].append({'time': reg_time,
                                                            'button': button})
        self.survey_information['result'][button] += 1

    def save_survey(self):
        """"""
        save_str = json.dumps(self.survey_information, indent=2, sort_keys=True)
        full_file_name = 'survey_information.txt'
        full_save_path = '%s/%s' % (self.save_path, full_file_name)
        with open(full_save_path, 'w+') as f:
            f.write(save_str)
        print 'Saving survey data to: ' + full_save_path

    def print_survey(self):
        total_clicks = 0
        for field in SURVEY_FIELDS:
            total_clicks += self.survey_information['result'][field.lower()]
        print 50 * '-'
        print 'Survey summary'
        for field in SURVEY_FIELDS:
            v = self.survey_information['result'][field.lower()]
            print '%d people (%.1f%%) thought the event was %s' % (v, 100.0 * v / total_clicks, field)
        print 50 * '-'

    def plot_pie_chart(self):
        # Plot data
        labels = [label.capitalize() for label in self.survey_information['result'].keys()]
        labels = sorted(labels)
        sizes = [self.survey_information['result'][label] for label in sorted(self.survey_information['result'].keys())]
        # colors red, green and yellow
        # Pop out the pie charts
        explode = (0.05, 0.05, 0.05)
        # Plot pie chart
        fig1, ax1 = plt.subplots()

        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return '{p:.1f}%  ({v:d})'.format(p=pct, v=val)

            return my_autopct
        _, texts, pct = ax1.pie(sizes, colors=PIE_COLOR, labels=labels, autopct=make_autopct(sizes), startangle=90,
                                explode=explode, pctdistance=0.7)
        # Set sizes of percentage and text
        [_.set_fontsize(14) for _ in pct]
        [_.set_fontsize(18) for _ in texts]
        # draw circle in the middle
        centre_circle = plt.Circle((0, 0), 0.5, fc='white')
        # plot text in the middle of the circle
        plt.text(-0.3, -0.075, "Result", fontsize=24, fontweight='bold')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.axis('equal')
        plt.tight_layout()
        print "Plot done"
        self.save_figure(fig, 'pie_chart.svg')
        plt.close('all')
        print "Figured saved"

    def save_figure(self, fig, fig_name):
        fig.savefig(os.path.join(self.save_path, 'images', fig_name), format='svg', dpi=1000)

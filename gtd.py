import os
import tempfile
temp_dir = tempfile.TemporaryDirectory()
os.environ['MPLCONFIGDIR'] = temp_dir.name

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import TwoLineListItem

from tradingeconomics.python.tradingeconomics.comtrade import getCmtTwoCountries
from tradingeconomics.python.tradingeconomics.glob import login

from datetime import date

from garden_matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import numpy as np


__author__ = 'Barnabas Okeke'
__copyright__ = '''Copyright (c) 2022 Barnabas Okeke.
All Rights Reserved.'''
__license__ = 'Proprietary'
__version__ = '0.0.1'

KV = '''
MDScreen:

    MDBoxLayout:
        
        MDTabs:
			allow_stretch: True
			tab_hint_x: True
			tab_padding: [1, 1, 1, 1]
			
			Tab:
				title: 'Export'
				
				MDScrollView:

					MDList:
						id: exportcontainer
			
			Tab:
				title: 'Import'
				
				MDScrollView:

					MDList:
						id: importcontainer
								
			Tab:
				title: 'Charts'
				
				MDTabs:
					allow_stretch: True
					tab_hint_x: True
	
					Tab:
						title: 'Export'
	
						MDBoxLayout:
							id: exportlinechart
							orientation: "vertical"
	
					Tab:
						title: 'Import'
	
						MDBoxLayout:
							id: importlinechart
							orientation: "vertical"
'''

class Tab(MDFloatLayout, MDTabsBase):
	pass


class GlobalTradeData(MDApp):

	i = 0 # Database hit counter
	j = 20 # Max number of times to hit the database
	k = 5 # Number of records to graph
	z = False # Set to 'True' to ignore 'j'
	from_country = 'Nigeria' # Originating country for trade
	to_country = 'United States' # Destination country for trade
	
	te_dic_data = []
	import_data = {}
	export_data = {}

	trade_year = date.today().year - 1

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.screen = Builder.load_string(KV)

		self.update_all()

	def update_all(self):
		self.update_data()

		self.update_export_charts()
		self.update_import_charts()

	def update_data(self):
		while True:
			try:
				login()
				self.te_dic_data = getCmtTwoCountries(
					country1=self.from_country,
					country2=self.to_country,
					page_number=self.i,
					output_type=None
				)
			except:
				break
			if len(self.te_dic_data) > 0:
				for data in self.te_dic_data:
					if (
						data.get('date') == self.trade_year
						and (
							data.get('type') == 'Export'
							or data.get('type') == 'Import'
						)
					):
						if not data.get('category') is None:
							if data.get('type') == 'Export':
								self.screen.ids.exportcontainer.add_widget(
									TwoLineListItem(
										text=f"{data.get('category')}",
										secondary_text=f"Value: {self.get_pos(data.get('value'))}"
									)
								)
								self.export_data.__setitem__(data.get('category'), data.get('value'))
							else:
								self.screen.ids.importcontainer.add_widget(
									TwoLineListItem(
										text=f"{data.get('category')}",
										secondary_text=f"Value: {self.get_pos(data.get('value'))}"
									)
								)
								self.import_data.__setitem__(data.get('category'), data.get('value'))

			self.i = self.i + 1
			if not self.z:
				if self.i > self.j:
					break
				
	def update_export_charts(self):
		export_categories = list(self.export_data.keys())[:self.k]
		export_values = list(self.export_data.values())[:self.k]

		x_pos_export = np.arange(len(export_categories))

		fig, axs = plt.subplots()
		axs.yaxis.set_major_formatter(
			lambda x,
				   pos: self.get_pos(x, '')
		)
		axs.plot(export_categories, export_values)
		axs.set_ylabel('Trade Values in US$')
		axs.set_xticks(x_pos_export, export_categories)
		plt.setp(
			axs.get_xticklabels(),
			rotation=90,
			ha="left",
			rotation_mode="anchor"
		)
		axs.tick_params(
			axis='x',
			direction='out',
			labelsize='small',
			pad=-6
		)
		axs.tick_params(
			axis='y',
			direction='out',
			labelsize='small',
		)
		self.screen.ids.exportlinechart.add_widget(FigureCanvasKivyAgg(figure=fig))

	def update_import_charts(self):
		import_categories = list(self.import_data.keys())[:self.k]
		import_values = list(self.import_data.values())[:self.k]

		x_pos_import = np.arange(len(import_categories))

		fig, axs = plt.subplots()
		axs.yaxis.set_major_formatter(
			lambda x,
				   pos: self.get_pos(x, '')
		)
		axs.plot(import_categories, import_values)
		axs.set_ylabel('Trade Values in US$')
		axs.set_xticks(x_pos_import, import_categories)
		plt.setp(
			axs.get_xticklabels(),
			rotation=90,
			ha="left",
			rotation_mode="anchor"
		)
		axs.tick_params(
			axis='x',
			direction='out',
			labelsize='small',
			pad=-6
		)
		axs.tick_params(
			axis='y',
			direction='out',
			labelsize='small',
		)
		self.screen.ids.importlinechart.add_widget(FigureCanvasKivyAgg(figure=fig))

	def get_pos(self, value, prefix='US$'):
		units = ['', 'K', 'M', 'B', 'T']
		factor = 1000.0
		value = float('{:.3g}'.format(value))
		unit_index = 0
		while abs(value) >= factor:
			unit_index = unit_index + 1
			value = value/factor
		return prefix + '{}{}'.format('{:f}'.format(value).rstrip('0').rstrip('.'), units[unit_index])

	def build(self):
		self.theme_cls.material_style = "M3"
		return self.screen


if __name__ == "__main__":
	copyright()
	print()
	print(__copyright__)
	print()
	GlobalTradeData().run()

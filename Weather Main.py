from WeatherData import WeatherData


def main():
    DataCollection = WeatherData()
    DataCollection.start()
    DataCollection.wrangle_data()
   	return


if __name__ == "__main__":
    main()


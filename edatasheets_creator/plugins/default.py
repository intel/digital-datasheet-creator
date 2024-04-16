# Default plugin class

class Plugin:
    # define static method, so no self parameter
    def process(self, num1, num2):
        print("Default Plugin is loaded in plugins subdirectory....")
        print(f"Numbers are {num1} and {num2}")

from Generators.DataBaseGenerator import  DataBaseGenerator

if __name__ == "__main__":
    number_of_samples = int(input('How many Samples do you want? \n'))

    print("############## Starting to Generate Sample Database ##############")
    generator = DataBaseGenerator()
    generator.generate(number_of_samples)
    print("############################ Finished ############################")

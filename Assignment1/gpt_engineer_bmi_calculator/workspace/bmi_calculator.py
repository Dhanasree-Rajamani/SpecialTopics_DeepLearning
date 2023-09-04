def calculate_bmi(weight, height):
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 2)

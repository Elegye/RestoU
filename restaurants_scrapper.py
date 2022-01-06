from bs4 import BeautifulSoup
import requests
import datetime

def CrousRestaurantsScrapper(url):
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    restaurantsContainer = soup.find("div", class_='list search resto current').find_all('li')

    restaurants = []

    for restaurant in restaurantsContainer:
        name = restaurant.find('h2').text
        link = restaurant.find('a', class_='link')['href']

        #print("Restaurant {} => {}".format(name, link))

        restaurants.append({
            "name": name,
            "link": link
        })
    
    return restaurants

def MenuScrapper(restaurant):
    print("Restaurant {}".format(restaurant["name"]))
    r = requests.get(restaurant['link'])
    soup = BeautifulSoup(r.content, 'html.parser')

    menus = soup.find('ul', class_='slides').findChildren(recursive=False)
    restaurant['menus'] = {}
    
    for menu in menus:
        day = menu.find('h3').text
        #print("Journée : {}".format(day))
        # Récupération des 3 repas du jour : Petit-Déjeuner / Déjeuner / Dîner.
        mealsContainer = menu.find('div', class_='content clearfix').find_all('div', recursive=False)
        meals = {}

        for meal in mealsContainer:
            mealName = meal.find('h4').text
            meals[mealName] = {}

            meal = meal.find('div', class_='content-repas')
            # We look for each span in the code. The span contains the formula name. The div after is a list of each plate.
            formulas = meal.find_all('span')
            for formula in formulas:
                name = formula.text
                next = formula.find_next('ul', class_='liste-plats')
                if next is None: #No formulas. Nothing is served during this meal.
                    meals[mealName][name] = None
                    continue
                else:
                    platesRaw = next.find_all('li')
                    meals[mealName][name] = [plate.text for plate in platesRaw] # Get plate as text

        restaurant['menus'][day] = meals
    
    return restaurant

if __name__ == '__main__':
    urls = [
        'https://www.crous-lorraine.fr/restauration/carte-restaurants/',
        'https://www.crous-nantes.fr/restauration/carte-des-restaurants/',
        'https://www.crous-normandie.fr/restauration/nos-structures-de-restauration/carte-des-restaurants/',
        'https://www.crous-paris.fr/restauration/les-lieux-de-restauration',
        'https://www.crous-lille.fr/restauration/carte-des-restaurants/',
        'https://www.crous-lyon.fr/restauration/manger-au-crous/nos-resto-u-nos-cafet-u/',
        'https://www.crous-nice.fr/restauration/localiser-les-cafeterias-et-restos-u/',
        'https://www.crous-bordeaux.fr/restauration/nosrestaurants/'
    ]
    start_time = datetime.datetime.now()
    for url in urls:
        restaurants = CrousRestaurantsScrapper(url)
        for restaurant in restaurants:
            MenuScrapper(restaurant)
    end_time = datetime.datetime.now()
    print("Durée d'éxecution : {}".format(end_time-start_time))
        

def clean_string(faker_category):
    # Si la chaîne est vide ou déjà correcte, on la retourne telle quelle
    #strip() pour enlever les espaces superflus
    faker_category = faker_category.rstrip(' ').replace('\n', '').strip()

    if not faker_category or (faker_category.startswith('[') and faker_category.endswith(']')):
        return faker_category

    # Si la chaîne commence par [ mais ne se termine pas par ]
    if faker_category.startswith('[') and not faker_category.endswith(']'):
        # On ajoute le ] manquant
        if faker_category.endswith(',"'):
            print("passe1")
            faker_category = faker_category[:-2] + ']'
        elif faker_category.endswith(', "'):
            print("passe2")
            faker_category = faker_category[:-3] + ']'
        elif faker_category.endswith(',  "'):
            print("passe3")
            faker_category = faker_category[:-4] + ']'
        elif faker_category.endswith(','):
            print("passe4")
            faker_category = faker_category[:-1] + ']'
        elif faker_category.endswith('"'):
            print("passe5")
            faker_category = faker_category + ']'
        else:
            print("passe6")
            faker_category = faker_category + '"]'
    else:
        # Cas où la chaîne ne commence pas par [, on l'ajoute
        faker_category = '["' + faker_category + '"]'

    return faker_category

# Test avec votre exemple
ex = '''[
  "5.5 pouces",
  "6.0 pouces",
  "6.1 pouces",
  "6.3 pouces",
  "6.5 pouces",
  "6.7 pouces",
  "6.8 pouces",
  "7.0 pouces",
  "7.2 pouces",
  "7.4 pouces",
  "7.6 pouces",
  "7.8 pouces",
  "8.0 pouces",
  "8.2 pouces",
  "8.4 pouces",
  "8.6 pouces",
  "8.8 pouces",
  "9.0 pouces",
  "9.2 pouces",
  "9.4 pouces",
  "9.6 pouces",
  " '''
print(clean_string(ex))

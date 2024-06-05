import requests 
from bs4 import BeautifulSoup 
import tkinter as tk 
from tkinter import messagebox, ttk 
import statistics 
import urllib.parse 
import webbrowser 

# Ziskanie detailu inzerátu zo zoznamu
def get_ad_details_from_list(ad_item):
    ad_info = {
        'URL': None, # Inicializace kluca 'URL' s hodnotou None
        'Cena v CZK': None # Inicializace klucaa 'Cena v CZK' s hodnotou None
    }

    # Extrahování URL 
    ad_url_tag = ad_item.find('a', href=True) # Najde první 'a' element s atributem href
    if ad_url_tag: # Pokud je nalezen tag 'a'
        ad_url = ad_url_tag['href'] # Ziska hodnotu atributu href
        ad_info['URL'] = ad_url # Ulozi URL do slovnika ad_info
        print(f"Found ad URL: {ad_info['URL']}") # Vypise najdenu URL

    # Extrahovani info o cene
    price_tag = ad_item.find('div', class_='notranslate c-item__price') # Najde  'div' s triedou 'notranslate c-item__price'
    if price_tag: 
        ad_info['Cena v CZK'] = price_tag.get_text(strip=True).replace('\xa0', ' ').replace('Kč', '').strip() # Ziska text, deletne unwanted znaky a 'Kč'
        print(f"Found ad price: {ad_info['Cena v CZK']} CZK") # vypise nalezenou cenu

    return ad_info # vrati slovnik s informacemi o inzeratu

# Funkce pro ziskanie inz z URL
def get_ads(category_url, max_pages=5): #Projedem 5 stran
    ads_info = [] 
    for page in range(1, max_pages + 1):
        url = f"{category_url}&strana={page}" 
        print(f"Accessing URL: {url}") 
        response = requests.get(url) 
        if response.status_code != 200: # Pokial web neda error 200
            print(f"Failed to access URL: {url}") 
            break 
        soup = BeautifulSoup(response.text, 'html.parser') # Parsuje HTML odpoved

        # Najde zoznam inzeratov
        ads_items = soup.find_all('li', class_='c-item') # Najde 'li' elementy s 'c-item'

        # Vylouceni sponzorovaných inzeratov
        preferred_list = soup.find('ul', class_='c-preferred-list__list') 
        if preferred_list: 
            sponsored_ads = preferred_list.find_all('li', class_='c-item')
            ads_items = [ad for ad in ads_items if ad not in sponsored_ads] # filtr sponzorované inzeráty

        if not ads_items: # Pokud nejsou nalezeny žádné inzeráty
            print("No ads found on this page.") # error msg
            break # koniec cyklu

        for ad_item in ads_items: 
            ad_info = get_ad_details_from_list(ad_item) 
            ads_info.append(ad_info) # prida informace o inzerátu do seznamu

    print(f"Total ads scraped: {len(ads_info)}") # vypise celkový počet získaných inzeratov
    return ads_info # vrati zoznam info o inzeratov

# funkcie pre  URL na základě parametrů
def build_url(make, model, year_from=None, year_to=None, variant=None, engine_capacity_from=None, engine_capacity_to=None, power_from=None, power_to=None):
    base_url = f'https://www.sauto.cz/inzerce/osobni/{make}/{model}' # základní URL
    params = [] 
    if year_from: 
        params.append(f"vyrobeno-od={year_from}") 
    if year_to: 
        params.append(f"vyrobeno-do={year_to}") 
    if variant: 
        encoded_variant = urllib.parse.quote(variant) 
        params.append(f"varianta={encoded_variant}") 
    if engine_capacity_from: 
        params.append(f"objem-od={engine_capacity_from}") 
    if engine_capacity_to: 
        params.append(f"objem-do={engine_capacity_to}") 
    if power_from: 
        params.append(f"vykon-od={power_from}kw") 
    if power_to: 
        params.append(f"vykon-do={power_to}kw") 
    if params: 
        return f"{base_url}?{'&'.join(params)}" 
    else: # Pokud nejsou přidány žádné parametry
        return base_url 

# Funkce pro provedení statistické analýzy
def analyze_prices(ads_info):
    prices = [int(ad['Cena v CZK'].replace(' ', '')) for ad in ads_info if ad['Cena v CZK']] 
    if prices: # ak su ceny
        max_price = max(prices) 
        min_price = min(prices) 
        median_price = statistics.median(prices) # Získá medián cen
        result_text = (
            f"Max Price: {max_price} CZK\n"
            f"Min Price: {min_price} CZK\n" 
            f"Median Price: {median_price} CZK\n" 
            "\nTop 5 Best Deals:\n" 
        )

        sorted_ads = sorted(ads_info, key=lambda x: int(x['Cena v CZK'].replace(' ', '')) if x['Cena v CZK'] else float('inf')) # inzeraty podle ceny
        for ad in sorted_ads[:5]: # top5
            result_text += f"{ad['Cena v CZK']} CZK - {ad['URL']}\n" 

        return result_text, sorted_ads[:5] # return text
    else:
        return "No valid prices found.", [] # error
# Funkce pro otevírání URL v webovém prohlížeči
def open_url(event):
    webbrowser.open_new(event.widget.tag_cget("hyperlink", "url")) # new url open

# Funkce pro zpracování události kliknutí na tlačítko
def on_search():
    make = make_combo.get().strip().lower() 
    model = model_combo.get().strip().lower() 
    year_from = year_from_combo.get().strip() 
    year_to = year_to_combo.get().strip() 
    variant = variant_combo.get().strip().lower() 
    engine_capacity_from = engine_capacity_from_entry.get().strip() 
    engine_capacity_to = engine_capacity_to_entry.get().strip() 
    power_from = power_from_entry.get().strip() 
    power_to = power_to_entry.get().strip() 
    url = build_url(make, model, year_from, year_to, variant, engine_capacity_from, engine_capacity_to, power_from, power_to) # Volám sestavení url
    ads_info = get_ads(url) # Volám ty reklamy
    result_text, top_deals = analyze_prices(ads_info) #  Volám statistiku
    display_results(result_text, top_deals) # Zobrazí výsledky v textovém widgetu
    print("Search completed") 


def display_results(text, top_deals):
    result_text_widget.config(state=tk.NORMAL) # Reset toho okna pro zapsání výsledků
    result_text_widget.delete(1.0, tk.END) 
    result_text_widget.insert(tk.END, text) 

    for ad in top_deals: # Tohle má vypsat výsledky
        start_index = result_text_widget.index(tk.END) 
        result_text_widget.insert(tk.END, ad['URL'] + "\n") 
        end_index = result_text_widget.index(tk.END) 
        result_text_widget.tag_add("hyperlink", start_index, end_index) # TO NEFUNGUJE
        result_text_widget.tag_config("hyperlink", foreground="blue", underline=True) # TO NEFUNGUJE
        result_text_widget.tag_bind("hyperlink", "<Button-1>", open_url) # TO NEFUNGUJE
        result_text_widget.tag_config("hyperlink", url=ad['URL']) # TO NEFUNGUJE

    result_text_widget.config(state=tk.DISABLED) 

# Tohle je jako __main__ ale pro tkinter, zavoláme na konci
root = tk.Tk() 
root.title("Car Search Tool") 

# Značky a modely aut pro dropdown menu
car_makes = ["Skoda"] # Seznam značek
car_models = {
    "Skoda": ["Fabia", "Octavia", "Superb"] # Seznam Modelů
}
car_variants = {
    "Skoda": { # Seznam Variant
        "Fabia": ["Active","Active Plus","Ambition","Ambition Plus","Style","Style Plus","Selection","Top Selection", "Monte Carlo"],
        "Octavia": ["Active","Active Plus","Ambition","Ambition Plus","Style","Style Plus","Style Exclusive","Laurin&Klement","Scout","RS","Sportline"],
        "Superb": ["Active","Active Plus","Ambition","Ambition Plus","Style","Style Plus","Laurin & Klement", "Sportline"]
    }
}


# Tyhle dvě aktualizují ty menu aby šli vybrat jen správný modely a varianty k správným autům, ne BMW Superb AMG
def update_models(event):
    selected_make = make_combo.get() 
    model_combo['values'] = car_models.get(selected_make, []) # Aktualizuje hodnoty v dropdown menu pro modely podle značky
    model_combo.set('')
    variant_combo['values'] = [] 
    variant_combo.set('') 

def update_variants(event):
    selected_make = make_combo.get()
    selected_model = model_combo.get()
    if selected_make and selected_model:
        variant_combo['values'] = car_variants.get(selected_make, {}).get(selected_model, []) # Aktualizuje hodnoty v dropdown menu pro varianty podle těch modelů
        variant_combo.set('') 

# Ta aplikace je grid a tohle na ní háže jednotlivý kostky
tk.Label(root, text="Car Make:").grid(row=0, column=0, padx=10, pady=10) 
make_combo = ttk.Combobox(root, values=car_makes) 
make_combo.grid(row=0, column=1, padx=10, pady=10) 
make_combo.bind("<<ComboboxSelected>>", update_models) 

tk.Label(root, text="Car Model:").grid(row=1, column=0, padx=10, pady=10) 
model_combo = ttk.Combobox(root) 
model_combo.grid(row=1, column=1, padx=10, pady=10) 
model_combo.bind("<<ComboboxSelected>>", update_variants) 

tk.Label(root, text="Year From:").grid(row=2, column=0, padx=10, pady=10) 
year_from_combo = ttk.Combobox(root, values=[str(year) for year in range(2000, 2025)]) 
year_from_combo.grid(row=2, column=1, padx=10, pady=10) 

tk.Label(root, text="Year To:").grid(row=3, column=0, padx=10, pady=10) 
year_to_combo = ttk.Combobox(root, values=[str(year) for year in range(2000, 2025)]) 
year_to_combo.grid(row=3, column=1, padx=10, pady=10) 

tk.Label(root, text="Variant:").grid(row=4, column=0, padx=10, pady=10)
variant_combo = ttk.Combobox(root) 
variant_combo.grid(row=4, column=1, padx=10, pady=10) 

tk.Label(root, text="Engine Capacity From (ccm):").grid(row=5, column=0, padx=10, pady=10) 
engine_capacity_from_entry = ttk.Combobox(root, values=[str(year) for year in range(0, 20000)]) 
engine_capacity_from_entry.grid(row=5, column=1, padx=10, pady=10) 

tk.Label(root, text="Engine Capacity To (ccm):").grid(row=6, column=0, padx=10, pady=10) 
engine_capacity_to_entry = ttk.Combobox(root, values=[str(year) for year in range(0, 20000)]) 
engine_capacity_to_entry.grid(row=6, column=1, padx=10, pady=10) 

tk.Label(root, text="Power From (kW):").grid(row=7, column=0, padx=10, pady=10) 
power_from_entry = ttk.Combobox(root, values=[str(year) for year in range(0, 2000)]) 
power_from_entry.grid(row=7, column=1, padx=10, pady=10) 

tk.Label(root, text="Power To (kW):").grid(row=8, column=0, padx=10, pady=10) 
power_to_entry = ttk.Combobox(root, values=[str(year) for year in range(0, 2000)]) 
power_to_entry.grid(row=8, column=1, padx=10, pady=10) 

search_button = tk.Button(root, text="Search", command=on_search) 
search_button.grid(row=9, column=0, columnspan=2, pady=20)

result_text_widget = tk.Text(root, state=tk.DISABLED, wrap=tk.WORD)
result_text_widget.grid(row=10, column=0, columnspan=2, pady=20) 

root.mainloop() # Spustí tkinter

import logging
import sys 
import datetime 
import re 
import json 
import os 

# --- ANSI ΧΡΩΜΑΤΑ (Σταθερές) ---
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

DATE_FORMAT = '%d/%m/%Y'

# Ρυθμίσεις Logging
logging.basicConfig(
    filename='error_log.txt', 
    level=logging.WARNING,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8' 
)

# -------------------- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ΣΤΟΙΧΙΣΗΣ --------------------
def katharismos_ansi(s):
    """Αφαιρεί τους κώδικες ANSI από μια συμβολοσειρά για να βρει το πραγματικό της μήκος."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)

def stoixisi(label_colored, value_colored, width):
    """Επιστρέφει μια γραμμή με σωστή στοίχιση, λαμβάνοντας υπόψη τους κώδικες ANSI."""
    label_len = len(katharismos_ansi(label_colored))
    padding = width - label_len
    return label_colored + " " * padding + value_colored

# -------------------- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ JSON/LOGGING --------------------
def get_monthly_filename(date_string):
    """Υπολογίζει το όνομα αρχείου JSON με βάση την ημερομηνία (π.χ. 'ergasia_log_11_2025.json')."""
    try:
        dt_object = datetime.datetime.strptime(date_string, DATE_FORMAT)
        return f'ergasia_log_{dt_object.month:02d}_{dt_object.year}.json'
    except ValueError:
        return 'fallback_log.json' 

def load_data_json(date_string):
    """Φορτώνει τα δεδομένα από το μηνιαίο αρχείο JSON με βάση την ημερομηνία."""
    log_file_name = get_monthly_filename(date_string)
    try:
        with open(log_file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Σφάλμα κατά τη φόρτωση του αρχείου JSON ({log_file_name}): {e}")
        print(f"{RED}⚠️ Σφάλμα στην ανάγνωση του αρχείου {log_file_name}. Επιστρέφεται κενή λίστα.{RESET}")
        return []

def save_data_json(data, date_string):
    """Αποθηκεύει τη λίστα δεδομένων στο μηνιαίο αρχείο JSON με βάση την ημερομηνία."""
    log_file_name = get_monthly_filename(date_string)
    try:
        with open(log_file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Σφάλμα κατά την αποθήκευση στο αρχείο JSON ({log_file_name}): {e}")
        print(f"{RED}❌ Αδυναμία αποθήκευσης των δεδομένων.{RESET}")
# -------------------------------------------------------------------------

def get_month_and_year():
    """Ζητάει από τον χρήστη τον μήνα (1-12) και προαιρετικά το έτος και επιστρέφει ημερομηνία '01/MM/YYYY'."""
    while True:
        try:
            # 1. Εισαγωγή Μήνα
            month_input = input(f"{BOLD}Εισάγετε τον αριθμό του μήνα (1-12):{RESET} ").strip()
            
            if not month_input or not month_input.isdigit():
                 print(f"{RED}❗ Παρακαλώ εισάγετε έναν αριθμό μήνα (1-12).{RESET}")
                 continue

            month = int(month_input)
            
            if not 1 <= month <= 12:
                print(f"{RED}❗ Άκυρος μήνας. Παρακαλώ εισάγετε αριθμό από 1 έως 12.{RESET}")
                continue
            
            # 2. Εισαγωγή Έτους
            current_year = datetime.date.today().year
            year_input = input(f"Εισάγετε το έτος (Άσε κενό για το {BOLD}{current_year}{RESET}): ").strip()
            
            if not year_input:
                year = current_year
            elif not year_input.isdigit() or len(year_input) != 4:
                print(f"{RED}❗ Μη έγκυρη μορφή έτους. Δώστε 4 ψηφία (π.χ. 2025).{RESET}")
                continue
            else:
                year = int(year_input)

            # 3. Κατασκευή Ημερομηνίας (1η του μήνα)
            date_string = f"01/{month:02d}/{year}"
            return date_string
            
        except Exception:
            print(f"{RED}❌ Προέκυψε ένα γενικό σφάλμα εισόδου. Ξαναπροσπαθήστε.{RESET}")


def get_valid_date():
    """Εμφανίζει το μενού επιλογής ημερομηνίας και επιστρέφει έγκυρη, μη μελλοντική ημερομηνία ή None, None για ακύρωση."""
    
    simerini_hmerominia_euro = datetime.date.today().strftime(DATE_FORMAT)
    date_to_log = None
    
    while date_to_log is None:
        print("\n" + f"{BOLD}{CYAN}" + "—"*40 + f"{RESET}")
        print(f"  {BOLD}📅 Επιλογή Ημερομηνίας Καταγραφής{RESET}")
        print(f"{BOLD}{CYAN}" + "—"*40 + f"{RESET}")
        print(f"  {GREEN}1. Καταγραφή για ΣΗΜΕΡΑ ({simerini_hmerominia_euro}){RESET}")
        print(f"  {YELLOW}2. Καταγραφή για ΑΛΛΗ ΗΜΕΡΟΜΗΝΙΑ (Παρελθόν){RESET}")
        print(f"  {RED}0. Ακύρωση & Επιστροφή στο Μενού{RESET}") # Επιλογή 0 για επιστροφή σε υπο-μενού
        print(f"{BOLD}{CYAN}" + "—"*40 + f"{RESET}")

        epilogi_date = input(f"👉 Δώσε την επιλογή σου (1, 2 ή 0): ").strip() 
        
        # --- 1. Χειρισμός Μη-Αριθμητικής/Ελλιπούς Εισόδου ---
        if not epilogi_date.isdigit() or not epilogi_date:
            print(f"{RED}❗ Λάθος επιλογή. Πρέπει να δώσετε τον αριθμό 1, 2 ή 0.{RESET}")
            continue

        epilogi_date_int = int(epilogi_date) # Μετατροπή σε ακέραιο

        if epilogi_date_int == 0: 
            print(f"{CYAN}☑️ Ακυρώθηκε η εισαγωγή δεδομένων.{RESET}")
            return None, None 
        
        if epilogi_date_int == 1:
            candidate_date = simerini_hmerominia_euro
        elif epilogi_date_int == 2:
            date_input = input(f"Εισάγετε Ημερομηνία (π.χ. {BOLD}01/01/2025{RESET}): ").strip()
            if not date_input:
                 print(f"{RED}❗ Η είσοδος δεν μπορεί να είναι κενή. Ξαναπροσπαθήστε.{RESET}")
                 continue
            candidate_date = date_input
        else:
            print(f"{RED}❗ Λάθος επιλογή. Παρακαλώ δώσε 1, 2 ή 0.{RESET}")
            continue 

        # --- 2. Έλεγχος Μορφής ---
        try:
            dt_object = datetime.datetime.strptime(candidate_date, DATE_FORMAT)
        except ValueError:
            print(f"{RED}❗ Μη έγκυρη μορφή ημερομηνίας: {candidate_date}. Πρέπει να είναι {BOLD}DD/MM/YYYY{RESET}{RED}.{RESET}")
            continue

        # --- 3. Έλεγχος Μέλλοντος ---
        if dt_object.date() > datetime.date.today():
            print(f"{RED}❌ Δεν μπορείς να καταγράψεις δεδομένα για μελλοντική ημερομηνία ({candidate_date}).{RESET}")
            continue

        # --- 4. Έλεγχος Διπλοκαταχώρησης ---
        existing_data = load_data_json(candidate_date) 
        existing_dates = {entry['ΗΜΕΡΟΜΗΝΙΑ'] for entry in existing_data if 'ΗΜΕΡΟΜΗΝΙΑ' in entry}
        
        if candidate_date in existing_dates:
            print(f"{RED}❌ Η ημερομηνία {BOLD}{candidate_date}{RESET}{RED} έχει ήδη καταγραφεί. Παρακαλώ εισάγετε νέα ημερομηνία.{RESET}")
            continue 

        # Αν περάσουν όλοι οι έλεγχοι
        return candidate_date, existing_data 


def eisagogi_dedomenon():
    """Παίρνει δεδομένα εργασίας, επικυρώνει την ημερομηνία και αποθηκεύει σε μηνιαίο JSON."""
    
    result = get_valid_date()
    # ΕΛΕΓΧΟΣ ΓΙΑ ΑΚΥΡΩΣΗ
    if result is None or result[0] is None: 
        return # Επιστροφή στο main menu
        
    date_to_log, existing_data = result
    
    print(f"Καταγραφή για: {date_to_log}")
    
    try:
        # --- ΕΠΙΚΥΡΩΣΗ & ΕΙΣΑΓΩΓΗ ΩΡΩΝ ΕΡΓΑΣΙΑΣ ---
        while True:
            try:
                wres = float(input("Ώρες εργασίας (Πάτα 0 για μη εργάσιμη ημέρα): "))
                if wres < 0:
                    print(f"{RED}❌ Οι ώρες εργασίας δεν μπορούν να είναι αρνητικές.{RESET}")
                else:
                    break 
            except ValueError:
                print(f"{RED}❌ Οι ώρες εργασίας πρέπει να είναι αριθμός.{RESET}")

        
        if wres == 0:
            # --- ΛΟΓΙΚΗ: ΑΥΤΟΜΑΤΗ ΚΑΤΑΓΡΑΦΗ ΜΗΔΕΝ & ΠΑΡΑΚΑΜΨΗ INPUT ---
            xiliometra = 0.0
            paralaves = 0
            paradoseis = 0
            print(f"{YELLOW}⚠️ Καταγράφεται ως μη εργάσιμη ημέρα (0 σε όλες τις ποσότητες).{RESET}")
        else:
            # --- ΣΥΝΗΘΗΣ ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ---
            xiliometra = float(input("Χιλιόμετρα οδήγησης: "))
            paralaves = int(input("Αριθμός παραλαβών: "))
            paradoseis = int(input("Αριθμός παραδόσεων: "))
            
        # 1. Δημιουργία νέας καταγραφής ως λεξικό
        new_entry = {
            "ΗΜΕΡΟΜΗΝΙΑ": date_to_log,
            "ΩΡΕΣ": wres,
            "ΧΙΛΙΟΜΕΤΡΑ": xiliometra,
            "ΠΑΡΑΛΑΒΕΣ": paralaves,
            "ΠΑΡΑΔΟΣΕΙΣ": paradoseis,
            "ΚΑΤΑΓΡΑΦΗ_ΣΕ": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 2. Προσθήκη στα ήδη φορτωμένα δεδομένα του μήνα και αποθήκευση
        existing_data.append(new_entry) 
        save_data_json(existing_data, date_to_log)
        
        log_file_name = get_monthly_filename(date_to_log)
        print(f"\n{GREEN}✅ Καταγραφή επιτυχής στο {log_file_name}.{RESET}")
        
    except ValueError:
        print(f"\n{RED}❌ Σφάλμα: Παρακαλώ εισάγετε αριθμούς (ή ακέραιους) για τις ποσότητες.{RESET}")
        logging.warning("Αποτυχία εισαγωγής δεδομένων: Μη έγκυρη αριθμητική τιμή σε Χιλιόμετρα/Παραλαβές/Παραδόσεις.")
        
    except Exception as e:
        logging.error(f"Σφάλμα κατά την εισαγωγή δεδομένων: {e}")
        print(f"\n{RED}❌ Προέκυψε ένα γενικό σφάλμα.{RESET}")

def epexergasia_dedomenon():
    """Εμφανίζει μήνυμα ότι η επεξεργασία δεδομένων είναι ακόμα υπό κατασκευή."""
    print(f"\n{CYAN}--- ⚙️ Επεξεργασία Δεδομένων ---{RESET}")
    print(f"{YELLOW}Η επεξεργασία δεδομένων είναι ακόμα υπό κατασκευή, όταν βγεί v2 θα σας ειδοποιήσουμε (μπορεί και όχι).{RESET}")


def provoli_dedomenon():
    """Διαβάζει τα δεδομένα από το επιλεγμένο μηνιαίο αρχείο JSON, υπολογίζει συνολικά στατιστικά και μέσους όρους και τα εμφανίζει."""
    
    print(f"\n{CYAN}--- 📊 Επιλογή Μήνα για Προβολή ---{RESET}")
    
    # ΒΗΜΑ 1: Ζητάμε από τον χρήστη να επιλέξει τον μήνα/έτος
    date_input = get_month_and_year()
    
    log_file_to_view = get_monthly_filename(date_input)
    data = load_data_json(date_input) # Φόρτωση του επιλεγμένου αρχείου

    if not data:
        print(f"{RED}❌ Το αρχείο δεδομένων ({log_file_to_view}) είναι άδειο ή δεν βρέθηκε.{RESET}")
        return

    # *** ΛΟΓΙΚΗ: ΤΑΞΙΝΟΜΗΣΗ ΔΕΔΟΜΕΝΩΝ ***
    try:
        data.sort(key=lambda entry: datetime.datetime.strptime(entry['ΗΜΕΡΟΜΗΝΙΑ'], DATE_FORMAT))
        print(f"{GREEN}✅ Τα δεδομένα ταξινομήθηκαν με επιτυχία.{RESET}")
    except Exception as e:
        logging.error(f"Αποτυχία ταξινόμησης δεδομένων: {e}")
        print(f"{RED}⚠️ Προσοχή: Αδυναμία ταξινόμησης των δεδομένων. Εμφανίζονται ως έχουν.{RESET}")
    # *****************************************

    LINE_WIDTH = 70
    LABEL_WIDTH = 32   
    
    print(f"\n{BOLD}{CYAN}" + "="*LINE_WIDTH)
    print("        📊  ΠΡΟΒΟΛΗ ΔΕΔΟΜΕΝΩΝ & ΑΝΑΛΥΤΙΚΑ ΣΤΑΤΙΣΤΙΚΑ  📈")
    print("="*LINE_WIDTH + f"{RESET}")
    
    synolo_wres = 0.0
    synolo_xiliometra = 0.0
    synolo_paralaves = 0
    synolo_paradoseis = 0
    
    # 1. Υπολογισμός Συνόλων
    for entry in data:
        try:
            synolo_wres += entry.get('ΩΡΕΣ', 0.0)
            synolo_xiliometra += entry.get('ΧΙΛΙΟΜΕΤΡΑ', 0.0)
            synolo_paralaves += entry.get('ΠΑΡΑΛΑΒΕΣ', 0)
            synolo_paradoseis += entry.get('ΠΑΡΑΔΟΣΕΙΣ', 0)
        except KeyError as e:
            logging.warning(f"Παραλείφθηκε καταγραφή λόγω ελλείποντος κλειδιού: {e} στο JSON.")
    
    arithmos_katagrafon = len(data)

    # 2. Υπολογισμός και Εκτύπωση Στατιστικών
    if arithmos_katagrafon > 0:
        avg_wres = synolo_wres / arithmos_katagrafon
        avg_xiliometra = synolo_xiliometra / arithmos_katagrafon
        avg_paralaves = synolo_paralaves / arithmos_katagrafon
        avg_paradoseis = synolo_paradoseis / arithmos_katagrafon
        
        # ΥΠΟΛΟΓΙΣΜΟΣ: Συνολικά Stops & Μέσος όρος Stops/Day
        synolo_stops = synolo_paralaves + synolo_paradoseis
        avg_stops_per_day = synolo_stops / arithmos_katagrafon

        print("\n" + f"{BOLD}{YELLOW}" + "—"*LINE_WIDTH)
        print(f"            ΣΥΝΟΛΙΚΑ ΣΤΑΤΙΣΤΙΚΑ ({arithmos_katagrafon} Καταγραφές)")
        print("—"*LINE_WIDTH + f"{RESET}")
        
        # ΕΚΤΥΠΩΣΗ ΣΥΝΟΛΩΝ (ΔΙΟΡΘΩΜΕΝΗ ΣΤΟΙΧΙΣΗ)
        def format_summary(label, value_str, width=LABEL_WIDTH):
             label_part = f"  {label}"
             return stoixisi(label_part, value_str, width)
        
        print(f"  {BOLD}ΣΥΝΟΛΑ:{RESET}")
        print(f"  {YELLOW}──────────────────────────────────────────────────────────{RESET}")
        
        print(format_summary(f"{GREEN}⌛ Συνολικές Ώρες Εργασίας:{RESET}", f"{synolo_wres:.1f} ώρες"))
        print(format_summary(f"{GREEN}🛣️ Συνολικά Χιλιόμετρα:{RESET}", f"{synolo_xiliometra:.1f} χλμ"))
        print(format_summary(f"{GREEN}📥 Συνολικές Παραλαβές:{RESET}", f"{synolo_paralaves} παραλαβές"))
        print(format_summary(f"{GREEN}📤 Συνολικές Παδόσεις:{RESET}", f"{synolo_paradoseis} παραδόσεις"))
        print(format_summary(f"{GREEN}📦 Συνολικά Στοπ :{RESET}", f"{synolo_stops} στοπ")) 

        print(f"\n  {BOLD}ΜΕΣΟΙ ΟΡΟΙ (Ανά Καταγραφή):{RESET}")
        print(f"  {YELLOW}──────────────────────────────────────────────────────────{RESET}")
        
        # ΕΚΤΥΠΩΣΗ ΜΕΣΩΝ ΟΡΩΝ
        print(format_summary(f"{CYAN}⏱️ Μέσος Όρος Ωρών:{RESET}", f"{avg_wres:.2f} ώρες"))
        print(format_summary(f"{CYAN}🗺️ Μέσος Όρος Χιλιομέτρων:{RESET}", f"{avg_xiliometra:.2f} χλμ"))
        print(format_summary(f"{CYAN}➕ Μέσος Όρος Παραλαβών:{RESET}", f"{avg_paralaves:.2f}"))
        print(format_summary(f"{CYAN}➖ Μέσος Όρος Παδόσεων:{RESET}", f"{avg_paradoseis:.2f}"))
        print(format_summary(f"{CYAN}🛑 Μέσος Όρος Στοπ/Ημέρα:{RESET}", f"{avg_stops_per_day:.2f}")) 

        print(f"{BOLD}{CYAN}" + "="*LINE_WIDTH + f"{RESET}")

    # 3. Εκτύπωση Αναλυτικών Δεδομένων σε μορφή Πίνακα
    WIDTHS = [12, 6, 11, 10, 10]
    HEADERS = ["ΗΜΕΡΟΜΗΝΙΑ", "ΩΡΕΣ", "ΧΙΛΙΟΜΕΤΡΑ", "ΠΑΡΑΛΑΒΕΣ", "ΠΑΡΑΔΟΣΕΙΣ"]
    
    TABLE_WIDTH = sum(WIDTHS) + (len(WIDTHS) * 3) + 1 

    print(f"\n{BOLD}--- 📜 ΑΝΑΛΥΤΙΚΗ ΚΑΤΑΓΡΑΦΗ ΗΜΕΡΩΝ ({arithmos_katagrafon}) ---{RESET}")
    print("-" * TABLE_WIDTH)
    
    header_line = f"{BOLD}{CYAN}"
    for i, header in enumerate(HEADERS):
        header_line += f"{header:<{WIDTHS[i]}} | "
    print(header_line[:-2] + f"{RESET}")
    print("-" * TABLE_WIDTH)
    
    for entry in data:
        row_output = (
            f"{YELLOW}{entry.get('ΗΜΕΡΟΜΗΝΙΑ', 'N/A'):<{WIDTHS[0]}}{RESET} | "
            f"{GREEN}{entry.get('ΩΡΕΣ', 0.0):<{WIDTHS[1]}.1f}{RESET} | "
            f"{GREEN}{entry.get('ΧΙΛΙΟΜΕΤΡΑ', 0.0):<{WIDTHS[2]}.1f}{RESET} | "
            f"{GREEN}{entry.get('ΠΑΡΑΛΑΒΕΣ', 0):<{WIDTHS[3]}}{RESET} | "
            f"{GREEN}{entry.get('ΠΑΡΑΔΟΣΕΙΣ', 0):<{WIDTHS[4]}}{RESET}"
        )
        print(row_output)

    print("-" * TABLE_WIDTH)


def emfanisi_menu():
    """Εμφανίζει το κεντρικό μενού με σωστή στοίχιση."""
    MENU_WIDTH = 45 
    TITLE_WIDTH = 38 
    MENU_TITLE = "💻 Μενού Καταγραφής Εργασίας 🚚"
    
    title_padding = " " * ((MENU_WIDTH - len(katharismos_ansi(MENU_TITLE))) // 2)

    print("\n" + f"{BOLD}{CYAN}" + "="*MENU_WIDTH + f"{RESET}")
    print(f"{title_padding}{MENU_TITLE}")
    print(f"{BOLD}{CYAN}" + "="*MENU_WIDTH + f"{RESET}")
    
    # Επιλογές 
    print(stoixisi(f"{GREEN}1. Εισαγωγή νέων δεδομένων{RESET}", f"{GREEN}📝{RESET}", TITLE_WIDTH))
    print(stoixisi(f"{YELLOW}2. Επεξεργασία δεδομένων{RESET}", f"{YELLOW}⚙️{RESET}", TITLE_WIDTH)) 
    print(stoixisi(f"{GREEN}3. Προβολή δεδομένων & Στατιστικά{RESET}", f"{GREEN}📊{RESET}", TITLE_WIDTH))
    # Η Επιλογή 4 (Κλείσιμο) αφαιρέθηκε από εδώ
    print(stoixisi(f"{RED}5. Διαγραφή Αρχείου Log (RESET){RESET}", f"{RED}💣{RESET}", TITLE_WIDTH)) 
    print(stoixisi(f"{RED}0. Κλείσιμο προγράμματος{RESET}", f"{RED}🛑{RESET}", TITLE_WIDTH)) # ΝΕΟ: Επιλογή 0 για έξοδο

    print(f"{BOLD}{CYAN}" + "="*MENU_WIDTH + f"{RESET}")

def main():
    """Ο βασικός βρόχος εκτέλεσης του προγράμματος."""
    while True:
        emfanisi_menu()
        
        # Το prompt ενημερώθηκε
        epilogi_str = input(f"{BOLD}👉 Δώσε την επιλογή σου (0, 1, 2, 3, 5):{RESET} ").strip() 
        
        try:
            epilogi = int(epilogi_str)
            
            if epilogi == 0: # ΝΕΟ: Έξοδος στο 0
                print(f"\n{RED}👋 Κλείσιμο προγράμματος. Καλό να περάσεις!{RESET}")
                sys.exit(0)
            elif epilogi == 1:
                eisagogi_dedomenon()
            elif epilogi == 2:
                epexergasia_dedomenon()
            elif epilogi == 3:
                provoli_dedomenon()
            elif epilogi == 5:
                # Προσωρινή λειτουργία διαγραφής
                print(f"{RED}⚠️ Η λειτουργία διαγραφής δεν είναι πλήρως υλοποιημένη για μηνιαία αρχεία. {RESET}")
                print(f"{RED}Παρακαλώ, διαγράψτε το αρχείο JSON του τρέχοντος μήνα χειροκίνητα (π.χ. ergasia_log_11_2025.json).{RESET}")
            else: # Ελέγχει την παλιά επιλογή 4 και άλλα άκυρα νούμερα
                print(f"\n{RED}❗ Λάθος επιλογή. Παρακαλώ δώσε έναν αριθμό (0, 1, 2, 3, ή 5).{RESET}")
        
        except ValueError:
            if epilogi_str: 
                # Χειρισμός μη αριθμητικής εισόδου
                print(f"\n{RED}❗ Λάθος είσοδος. Πρέπει να δώσεις έναν αριθμό (0, 1, 2, 3, ή 5).{RESET}")

if __name__ == "__main__":
    main()
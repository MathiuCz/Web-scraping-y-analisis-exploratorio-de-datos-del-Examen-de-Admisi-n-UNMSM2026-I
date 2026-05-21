from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# CONFIG EDGE

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 30)

BASE_URL = "https://admision.unmsm.edu.pe/Website20261/A/A.html"


# OBTENCIÓN DE LAS ESCUELAS

driver.get(BASE_URL)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))

escuelas = []
for a in driver.find_elements(By.TAG_NAME, "a"):
    texto = a.text.strip()
    href = a.get_attribute("href")
    if texto and href and href.endswith(".html"):
        escuelas.append((texto, href))

print(f"Escuelas encontradas: {len(escuelas)}")


# SCRAPING

resultados = []

for escuela, link in escuelas:
    print(f"Procesando: {escuela}")
    driver.get(link)

    try:
        
        wait.until(EC.presence_of_element_located((By.ID, "tablaPostulantes_wrapper")))
    except:
        print("No hay tabla en esta página")
        continue

    time.sleep(1)

      #Mostrar todos los registros
    driver.execute_script("""
        if ($.fn.DataTable.isDataTable('#tablaPostulantes')) {
            $('#tablaPostulantes').DataTable().page.len(-1).draw();
        }
    """)

    time.sleep(2)

    filas = driver.find_elements(By.CSS_SELECTOR, "#tablaPostulantes tbody tr")

    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        if len(celdas) < 6:
            continue

        resultados.append({
            "codigo": celdas[0].text.strip(),
            "nombre_apellido": celdas[1].text.strip(),
            "escuela": celdas[2].text.strip(),
            "puntaje": celdas[3].get_attribute("data-score"),
            "orden_merito": celdas[4].get_attribute("data-merit"),
            "observacion": celdas[5].text.strip()
        })

driver.quit()


# GUARDAR RESULTADOS

df = pd.DataFrame(resultados)

print(f"Total registros extraídos: {len(df)}")

df.to_csv("resultados_admision_unmsm.csv", index=False, encoding="utf-8-sig")
df.to_excel("resultados_admision_unmsm.xlsx", index=False)

print("SCRAPING COMPLETADO. Resultados guardados en CSV y Excel.")


df_unmsm = pd.read_csv('resultados_admision_unmsm.csv')

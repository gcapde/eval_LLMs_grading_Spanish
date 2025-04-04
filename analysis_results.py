# -*- coding: utf-8 -*-
import sys
import os

import subprocess
import json

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
import matplotlib.pyplot as plt

import re
# import hashlib

# Función para crear un hash corto de una etiqueta larga
def shorten_label(label, length=10):
    # return hashlib.sha256(label.encode()).hexdigest()[:length]
    return f'words{len(label)}'

# Función para extraer la palabra clave correcta de actual_output
def extract_key_word(output, cnt_mal):
    # keywords = ["EXCELENTE", "ACEPTABLE", "INCORRECTA", "Excelente", "Aceptable", "Incorrecta"]
    keywords = ["Calificación: EXCELENTE", "Calificación: ACEPTABLE", "Calificación: INCORRECTA", "Calificación: Excelente", "Calificación: Aceptable", "Calificación: Incorrecta"]
    lower_output = output
    for word in keywords:
        if word in lower_output:
            return word.split(' ')[1].upper(), cnt_mal
            #return word.upper(), cnt_mal
    cnt_mal += 1
    return None, cnt_mal  # Retorna None si no encuentra ninguna palabra clave

# Función para limpiar los nombres de archivos
def clean_filename(filename):
    filename = filename.removeprefix('ollama:chat:')
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Funcion para convertir nombres de modelos para las graficas
def format_model_name(model_name):
    if model_name == "mistral_7b":
        model_name = "Mistral - 7B"
    if model_name == "llama3":
        model_name = "Llama 3 - 8B"
    if model_name == "llama3.1":
        model_name = "Llama 3.1 - 8B"
    if model_name == "gemma2_2b":
        model_name = "Gemma 2 - 2B"
    if model_name == "gemma2":
        model_name = "Gemma 2 - 9B"
    if model_name == "llama3.2_1b":
        model_name = "Llama 3.2 - 1B"
    if model_name == "llama3.2":
        model_name = "Llama 3.2 - 3B"
    if model_name == "llama3.3":
        model_name = "Llama 3.3 - 70B"
    if model_name == "llama3_70b":
        model_name = "Llama 3 - 70B"
    if model_name == "openai_gpt-4o":
        model_name = "GPT-4o"
    if model_name == "openai_gpt-4o-2024-08-06":
        model_name = "GPT-4o"
    if model_name == "openai_gpt-4-turbo-2024-04-09":
        model_name = "GPT-4"
    if model_name == "openai_gpt-4o-mini-2024-07-18":
        model_name = "GPT-4o-mini"
    if model_name == "phi3_14b":
        model_name = "Phi-3 - 14B"
    if model_name == "qwen2_72b":
        model_name = "Qwen 2 - 72B"
    if model_name == "qwen2":
        model_name = "Qwen 2 - 7B"
    if model_name == "qwen2.5":
        model_name = "Qwen 2.5 - 7B"
    if model_name == "qwen2.5_72b":
        model_name = "Qwen 2.5 - 72B"

    return model_name

def analizar_output(ruta_output):
    try:
        with open(ruta_output, 'r', encoding='utf-8') as archivo:
            data = json.load(archivo)

        # Crear un directorio para guardar las matrices de confusión si no existe
        output_dir = 'matrices'
        os.makedirs(output_dir, exist_ok=True)

        # Extraer la información y agrupar por modelo
        model_results = {}
        cnt_mal = 0

        for result in data['results']['results']:
            try:
                provider = result['provider']['id']
                prompt_label = result['prompt']['label']

                # Limpio el provider para que quede solo el modelo.
                provider = clean_filename(provider)
                
                # Generar una versión abreviada del prompt label
                short_label = shorten_label(prompt_label)

                if 'response' not in result or 'output' not in result['response']:
                    print(f"Registro omitido para el proveedor {provider} debido a falta de datos en output.")
                    continue
                
                actual_output = result['response']['output']

                # Extraer la palabra clave de actual_output
                extracted_output, cnt_mal = extract_key_word(actual_output, cnt_mal)
                if extracted_output is None:
                    print(f"Registro omitido para el proveedor {provider} debido a que no contiene una palabra clave válida en actual_output.\nOutput: {actual_output[:10]}")
                    extracted_output = actual_output
                    continue

                if 'vars' not in result or 'categoria' not in result['vars'] or not result['vars']['categoria']:
                    print(f"Registro omitido para el proveedor {provider} debido a falta de datos en vars.categoria.")
                    continue
                
                expected_output = result['vars']['categoria']

                if provider not in model_results:
                    model_results[provider] = {}

                if short_label not in model_results[provider]:
                    model_results[provider][short_label] = {'expected': [], 'actual': []}
                
                model_results[provider][short_label]['expected'].append(expected_output)
                model_results[provider][short_label]['actual'].append(extracted_output)
            
            except KeyError as e:
                print(f"Error al procesar el registro para el proveedor {provider}: {e}")
                continue
            
        print(f'Cantidad de registros mal: {cnt_mal}')
        # Crear la matriz de confusión para cada modelo y prompt label
        for provider, prompts in model_results.items():
            for short_label, outputs in prompts.items():
                expected = outputs['expected']
                actual = outputs['actual']
                
                labels = ["EXCELENTE", "ACEPTABLE", "INCORRECTA"]
                cm = confusion_matrix(expected, actual, labels=labels)
                accuracy = accuracy_score(expected, actual)

                disp_labels = ["EXCELLENT", "ACCEPTABLE", "INCORRECT"]
                disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=disp_labels)
                
                print(f"Matriz de Confusión para el modelo {provider} y el prompt {short_label}:")
                print(cm)
                print(f"Accuracy para el modelo {provider} y el prompt {short_label}: {100*accuracy:.2f}")

                disp.plot(cmap=plt.cm.Blues)
                #plt.title(f'Matriz de Confusión para {provider}\nPrompt: {short_label}')

                plt.tight_layout()
                plt.ylabel('True label')
                plt.xlabel('Predicted Label')
                plt.ylabel('True label')
                #plt.title(f'{format_model_name(provider)}')
                plt.tight_layout()

                # plt.show()

                # Guardar la figura de la matriz de confusión
                output_file = os.path.join(output_dir, f'cm_{provider}_{short_label}.pdf')
                plt.savefig(output_file)
                plt.close()  # Cerrar la figura para liberar memoria

    except Exception as e:
        print(f"Error al analizar el output: {e}")

if __name__ == "__main__":
    print("Run promptfoo Eval.")


    # Ruta del directorio que deseas listar
    ruta_directorio = "./"

    # Recorre todos los archivos y carpetas en el directorio
    # for archivo in os.listdir(ruta_directorio):
    #for archivo in ['openai_corregido.json']:
    #for archivo in ['modelos_grande_llama3.3_corregido.json']:
    #for archivo in ['modelos_medianos_corregido.json']:
    for archivo in ['modelos_chicos_corregido.json']:
        if archivo.endswith(".json") and os.path.isfile(os.path.join(ruta_directorio, archivo)):
            print("Analizando:",archivo)
            analizar_output(archivo)
            print("")

    # output = "modelos_chicos_corregido.json"
    # analizar_output(output)
    # output = "experiments_results.json"
    # output = "experiments_results_gemma2.json"
    # output = "experiments_results_llama70b.json"
    # output = "experiments_results_openAI.json"
    # output = "experiments_results_inverted_prompt.json"
    # analizar_output(output)

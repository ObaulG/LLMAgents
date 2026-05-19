#!/usr/bin/env python3
"""
Script étendu pour tester les sessions RAG :
1. Création de session et ajout d'historique dans le prompt
2. Récupération d'une ancienne session par le client JS
3. Affichage correct des anciens messages
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:8000"
DOCUMENT_ID = "8a672d2ae6f2abfa4434e0f4145a9aa77bbc6d56"
MODEL = "mistral-small"
QUESTIONS_FILE = "test-questions-rag.txt"
RESPONSES_FILE = "reponses-test-rag-8a672d2a-extended.txt"
SESSION_FILE = "session-8a672d2a-extended.json"

# Paramètres par défaut pour les requêtes
DEFAULT_PARAMS = {
    "k": 3,
    "use_rag": True,
    "use_reranking": False,
    "include_quantitative": False,
    "use_ontology_enrichment": False,
    "rag_monodocument_id": DOCUMENT_ID,
}


def create_session():
    """Créer une nouvelle session RAG pour le document via /api/sessions/rag/init/{document_id}."""
    url = f"{BASE_URL}/api/sessions/rag/init/{DOCUMENT_ID}"
    payload = {"premade_session": True}
    response = requests.get(url, json=payload)
    response.raise_for_status()
    return response.json()


def read_questions(filename):
    """Lire les questions depuis un fichier texte."""
    with open(filename, "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]
    return questions


def ask_question(question, session_id):
    """Envoyer une question à l'API RAG monodocument."""
    url = f"{BASE_URL}/api/query/single-doc-rag"
    payload = {
        **DEFAULT_PARAMS,
        "question": question,
        "models": [MODEL],
        "session_id": session_id,
    }
    
    print(f"  Question: {question}")
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def export_session(session_id):
    """Exporter la session via /api/sessions/rag/export/{session_id}."""
    url = f"{BASE_URL}/api/sessions/rag/export/{session_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_session(session_id):
    """Récupérer une session RAG existante via l'API (comme le fait le client JS)."""
    url = f"{BASE_URL}/api/sessions/rag/{session_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def format_response(question, data, question_num):
    """Formater une réponse pour l'affichage/sauvegarde."""
    answer = data.get("answer", "")
    sources = data.get("sources", [])
    total_time = data.get("total_time", 0)
    metadata = data.get("metadata", {})
    model = metadata.get("model", MODEL)
    
    formatted = f"=== Question {question_num} ===\n"
    formatted += f"Q: {question}\n"
    formatted += f"A: {answer}\n"
    formatted += f"Model: {model}\n"
    formatted += f"Time: {total_time}s\n"
    formatted += "Sources:\n"
    for i, source in enumerate(sources or [], 1):
        formatted += f"  {i}. {source}\n"
    formatted += "\n"
    return formatted


def verify_session_for_js_display(session_data):
    """
    Vérifie qu'une session RAG a le bon format pour être affichée par le client JS.
    Le client JS (rebuildSessionInChat) attend une structure avec :
    - session_id
    - document_id
    - interactions: liste d'objets avec question, answer, sources, model, k, use_reranking, total_time
    
    Retourne (success: bool, errors: list, warnings: list)
    """
    errors = []
    warnings = []
    
    # Vérifier la structure de base
    required_fields = ['session_id', 'document_id', 'interactions']
    for field in required_fields:
        if field not in session_data:
            errors.append(f"Champ manquant: {field}")
    
    if 'interactions' not in session_data:
        return False, errors, warnings
    
    interactions = session_data['interactions']
    if not isinstance(interactions, list):
        errors.append("interactions doit être une liste")
        return False, errors, warnings
    
    if len(interactions) == 0:
        warnings.append("Aucune interaction trouvée dans la session")
    
    # Vérifier chaque interaction
    interaction_required = ['question', 'answer', 'sources', 'model', 'k', 'total_time']
    for idx, interaction in enumerate(interactions):
        for field in interaction_required:
            if field not in interaction:
                errors.append(f"Interaction {idx}: champ manquant: {field}")
        
        # Vérifier les types
        if 'question' in interaction and not isinstance(interaction['question'], str):
            errors.append(f"Interaction {idx}: question doit être une chaîne")
        if 'answer' in interaction and not isinstance(interaction['answer'], str):
            errors.append(f"Interaction {idx}: answer doit être une chaîne")
        if 'sources' in interaction and not isinstance(interaction['sources'], list):
            errors.append(f"Interaction {idx}: sources doit être une liste")
        if 'model' in interaction and not isinstance(interaction['model'], str):
            errors.append(f"Interaction {idx}: model doit être une chaîne")
        if 'k' in interaction and not isinstance(interaction['k'], int):
            errors.append(f"Interaction {idx}: k doit être un entier")
        if 'total_time' in interaction and not isinstance(interaction['total_time'], (int, float)):
            errors.append(f"Interaction {idx}: total_time doit être un nombre")
    
    success = len(errors) == 0
    return success, errors, warnings


def simulate_js_display(session_data):
    """
    Simule l'affichage du client JS (rebuildSessionInChat).
    Retourne une représentation textuelle de ce que le client JS afficherait.
    """
    display = []
    display.append(f"=== Session {session_data.get('session_id', 'N/A')} ===")
    display.append(f"Document: {session_data.get('document_id', 'N/A')}")
    display.append(f"Nombre d'interactions: {len(session_data.get('interactions', []))}")
    display.append("")
    
    interactions = session_data.get('interactions', [])
    for idx, interaction in enumerate(interactions):
        display.append(f"--- Interaction {idx + 1} ---")
        display.append(f"User: {interaction.get('question', 'N/A')}")
        display.append(f"Bot: {interaction.get('answer', 'N/A')}")
        
        sources = interaction.get('sources', [])
        if sources:
            display.append(f"Sources ({len(sources)}):")
            for src_idx, source in enumerate(sources):
                if isinstance(source, dict):
                    content = source.get('content', 'N/A')
                    score = source.get('score_cossim', 'N/A')
                    display.append(f"  {src_idx + 1}. Score: {score} - {content[:50]}...")
                else:
                    display.append(f"  {src_idx + 1}. {str(source)[:50]}...")
        
        model = interaction.get('model', 'N/A')
        k = interaction.get('k', 'N/A')
        total_time = interaction.get('total_time', 'N/A')
        display.append(f"Meta: model={model}, k={k}, time={total_time}s")
        display.append("")
    
    return "\n".join(display)


def test_session_retrieval_and_display(session_id):
    """
    Test principal: vérifie que le client JS peut récupérer une session
    et afficher correctement les anciens messages.
    
    Retourne (success: bool, message: str)
    """
    print("\n" + "="*60)
    print("TEST: Récupération et affichage d'une session existante")
    print("="*60)
    
    try:
        # Étape 1: Récupérer la session via l'API (comme le fait fetchRAGSession)
        print(f"\n1. Récupération de la session {session_id}...")
        session_data = get_session(session_id)
        print(f"   Session récupérée avec succès")
        
        # Étape 2: Sauvegarder la session dans un fichier JSON
        print(f"\n2. Sauvegarde de la session dans {SESSION_FILE}...")
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        print(f"   Session sauvegardée")
        
        # Étape 3: Vérifier le format pour le client JS
        print(f"\n3. Vérification du format pour le client JS...")
        success, errors, warnings = verify_session_for_js_display(session_data)
        
        if not success:
            return False, f"Erreurs de format: {errors}"
        
        if warnings:
            print(f"   ⚠ Avertissements: {warnings}")
        print(f"   ✓ Format valide pour le client JS")
        
        # Étape 4: Simuler l'affichage
        print(f"\n4. Simulation de l'affichage client JS:")
        display_output = simulate_js_display(session_data)
        print(display_output)
        
        # Étape 5: Vérifier que chaque interaction a les champs nécessaires
        print(f"\n5. Vérification détaillée des interactions:")
        interactions = session_data.get('interactions', [])
        for idx, interaction in enumerate(interactions):
            has_all = all(k in interaction for k in ['question', 'answer', 'sources', 'model'])
            status = "✓" if has_all else "✗"
            print(f"   {status} Interaction {idx + 1}: {len(interaction.get('sources', []))} sources, modèle: {interaction.get('model', 'N/A')}")
        
        return True, "Toutes les vérifications ont réussi"
        
    except Exception as e:
        return False, f"Erreur: {str(e)}"


def main():
    print("Démarrage du test RAG monodocument étendu...")
    print(f"Document: {DOCUMENT_ID}")
    print(f"Modèle: {MODEL}")
    
    # Étape 1: Créer une session
    print("\n" + "="*60)
    print("ÉTAPE 1: Création de la session")
    print("="*60)
    session_id = create_session()
    print(f"   Session créée: {session_id}")
    
    # Étape 2: Lire les questions
    print("\n" + "="*60)
    print("ÉTAPE 2: Lecture des questions")
    print("="*60)
    questions = read_questions(QUESTIONS_FILE)
    print(f"   {len(questions)} questions chargées")
    
    # Étape 3: Poser chaque question
    print("\n" + "="*60)
    print("ÉTAPE 3: Envoi des questions")
    print("="*60)
    all_responses = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n  [{i}/{len(questions)}]")
        try:
            data = ask_question(question, session_id)
            all_responses.append(format_response(question, data, i))
            time.sleep(1)
        except Exception as e:
            print(f"    Erreur: {e}")
            all_responses.append(f"=== Question {i} ===\nQ: {question}\nA: [ERREUR: {str(e)}]\n\n")
    
    # Étape 4: Sauvegarder les réponses
    print("\n" + "="*60)
    print("ÉTAPE 4: Sauvegarde des réponses")
    print("="*60)
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(all_responses))
    print(f"   Réponses sauvegardées dans {RESPONSES_FILE}")
    
    # Étape 5: Exporter la session (CSV)
    print("\n" + "="*60)
    print("ÉTAPE 5: Export de la session (CSV)")
    print("="*60)
    session_data_csv = export_session(session_id)
    csv_file = f"rag_sessions_csv/{session_id}.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(session_data_csv)
    print(f"   Session exportée en CSV: {csv_file}")
    
    # ÉTAPE 6: TEST DE RÉCUPÉRATION (NOUVEAU)
    print("\n" + "="*60)
    print("ÉTAPE 6: Test de récupération et affichage par le client JS")
    print("="*60)
    
    # Attendre un peu pour que la session soit bien sauvegardée
    time.sleep(2)
    
    test_success, test_message = test_session_retrieval_and_display(session_id)
    
    print("\n" + "="*60)
    print("RÉSULTAT DU TEST ÉTENDU")
    print("="*60)
    if test_success:
        print("✓ SUCCÈS: Le client JS peut récupérer et afficher la session")
        print(f"  {test_message}")
    else:
        print("✗ ÉCHEC: Problème détecté")
        print(f"  {test_message}")
    
    print("\nTest étendu terminé!")
    return test_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

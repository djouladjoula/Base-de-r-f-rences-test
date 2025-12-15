import streamlit as st
import pandas as pd
from openpyxl import Workbook
from io import BytesIO

st.set_page_config(page_title="Cyber Requirement Tagging", layout="wide")

st.title("🔐 Chatbot de catégorisation d’exigences de sécurité")
st.markdown("Outil de test – Génération automatique du fichier **Base de références test**")

# -----------------------------
# Upload BASE DE TAG
# -----------------------------
st.header("1️⃣ Charger la base de tags")
tags_file = st.file_uploader(
    "Fichier Excel : Taxonomie_exigences_securite_ID_Arbo",
    type=["xlsx"]
)

# -----------------------------
# Exigence utilisateur
# -----------------------------
st.header("2️⃣ Saisir l’exigence de sécurité")
exigence = st.text_area("Exigence", height=120)

# -----------------------------
# Placeholder analyse IA
# -----------------------------
def analyze_exigence_vs_tags(exigence_text, tags_df):
    """
    Fonction placeholder.
    À remplacer par appel LLM / moteur IA.
    Retour attendu :
    dict { tag_id: (niveau, justification) }
    """

    results = {}
    for _, row in tags_df.iterrows():
        tag_id = row["ID"]
        tag_name = row["TAG"]

        # LOGIQUE TEMPORAIRE (à remplacer)
        niveau = 0
        justification = "Aucun lien identifié entre ce tag et l’exigence."

        if tag_name.lower() in exigence_text.lower():
            niveau = 4
            justification = (
                "Correspondance directe : l’exigence traite explicitement "
                f"du thème couvert par le tag « {tag_name} »."
            )

        results[tag_id] = (niveau, justification)

    return results

# -----------------------------
# Bouton lancement
# -----------------------------
st.header("3️⃣ Lancer la catégorisation")

if st.button("🚀 Générer le fichier Excel"):

    if tags_file is None or not exigence.strip():
        st.error("❌ Veuillez charger la base de tags et saisir une exigence.")
    else:
        # Lecture base de tags
        tags_df = pd.read_excel(tags_file)

        # Filtrage lignes valides
        tags_df = tags_df.dropna(
            subset=["CATEGORIE", "TAG", "DESCRIPTION"],
            how="all"
        )

        # Analyse
        analysis_results = analyze_exigence_vs_tags(exigence, tags_df)

        # Création workbook
        wb = Workbook()

        # -----------------------------
        # ONGLET REFERENCES
        # -----------------------------
        ws_ref = wb.active
        ws_ref.title = "REFERENCES"

        headers = ["ID", "référentiel", "ID Exigence", "Exigence"]
        for tag_id in tags_df["ID"]:
            headers.append(f"Niveau Tag {tag_id}")
            headers.append(f"Justification Tag {tag_id}")

        ws_ref.append(headers)

        row = [1, "N/A", "N/A", exigence]
        for tag_id in tags_df["ID"]:
            niveau, justification = analysis_results[tag_id]
            row.extend([niveau, justification])

        ws_ref.append(row)

        # -----------------------------
        # ONGLET CROISEMENT
        # -----------------------------
        ws_cross = wb.create_sheet(title="CROISEMENT")

        ws_cross["A1"] = "Exigence"
        ws_cross["B1"] = exigence

        ws_cross.append([])
        ws_cross.append([])
        ws_cross.append(["ID", "Tag", "Niveau Tag", "Justification Tag"])

        for _, row in tags_df.iterrows():
            tag_id = row["ID"]
            tag_name = row["TAG"]
            niveau, justification = analysis_results[tag_id]

            if niveau > 0:
                ws_cross.append([tag_id, tag_name, niveau, justification])

        # -----------------------------
        # Export fichier
        # -----------------------------
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        st.success("✅ Fichier généré avec succès")

        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=output,
            file_name="Base de références test.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catégorisation Exigences Sécurité", layout="wide")

st.title("🔐 Chatbot IA – Catégorisation des exigences de sécurité")

# ==============================
# 1. Chargement du fichier TAGS
# ==============================

TAGS_FILE = "Taxonomie_exigences_securite_ID_Arbo.xlsx"

try:
    tags_df = pd.read_excel(TAGS_FILE)
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier de taxonomie : {e}")
    st.stop()

# ==============================
# 2. Normalisation des colonnes
# ==============================

tags_df.columns = (
    tags_df.columns
    .astype(str)
    .str.strip()
    .str.upper()
    .str.replace("\n", " ")
)

# ==============================
# 3. Détection intelligente des colonnes
# ==============================

EXPECTED_COLUMNS = {
    "CATEGORIE": ["CATEGORIE", "CATEGORY", "DOMAINE"],
    "TAG": ["TAG", "LIBELLE", "INTITULE", "EXIGENCE"],
    "DESCRIPTION": ["DESCRIPTION", "DESC", "DETAIL", "COMMENTAIRE"]
}

column_map = {}

for logical_col, aliases in EXPECTED_COLUMNS.items():
    for col in tags_df.columns:
        if col in aliases:
            column_map[logical_col] = col
            break

missing_cols = set(EXPECTED_COLUMNS.keys()) - set(column_map.keys())
if missing_cols:
    st.error(
        f"Colonnes obligatoires introuvables dans le fichier : {missing_cols}"
    )
    st.stop()

# Renommage standard
tags_df = tags_df.rename(columns={
    column_map["CATEGORIE"]: "CATEGORIE",
    column_map["TAG"]: "TAG",
    column_map["DESCRIPTION"]: "DESCRIPTION"
})

# ==============================
# 4. Nettoyage des lignes vides
# ==============================

tags_df = tags_df.dropna(
    subset=["CATEGORIE", "TAG", "DESCRIPTION"],
    how="all"
)

for col in ["CATEGORIE", "TAG", "DESCRIPTION"]:
    tags_df[col] = tags_df[col].astype(str).str.strip()

# ==============================
# 5. Vérification visuelle (debug)
# ==============================

with st.expander("🔍 Aperçu de la base de tags utilisée"):
    st.dataframe(tags_df, use_container_width=True)

st.success(f"✅ {len(tags_df)} tags de sécurité chargés et prêts à l’analyse")

# ==============================
# 6. Saisie de l'exigence
# ==============================

exigence = st.text_area(
    "✍️ Saisissez l’exigence de sécurité à catégoriser",
    height=150
)

# ==============================
# 7. Analyse IA (MVP – règles simples)
# ==============================

def score_exigence(exigence, tag, description):
    exigence = exigence.lower()
    tag = tag.lower()
    description = description.lower()

    if tag in exigence:
        return 4, "Correspondance directe : le tag est explicitement mentionné dans l’exigence."
    if any(word in exigence for word in tag.split()):
        return 3, "Correspondance forte : thématique du tag directement liée à l’exigence."
    if any(word in exigence for word in description.split()):
        return 2, "Lien indirect : le tag est pertinent dans le contexte général de l’exigence."
    return 0, "Aucun lien direct ou indirect identifié avec l’exigence."

# ==============================
# 8. Lancement de l’analyse
# ==============================

if st.button("🚀 Lancer la catégorisation"):
    if not exigence.strip():
        st.warning("Merci de saisir une exigence de sécurité.")
        st.stop()

    results = []

    for idx, row in tags_df.iterrows():
        niveau, justification = score_exigence(
            exigence,
            row["TAG"],
            row["DESCRIPTION"]
        )

        if niveau > 0:
            results.append({
                "ID Tag": idx + 1,
                "Catégorie": row["CATEGORIE"],
                "Tag": row["TAG"],
                "Niveau de pertinence": niveau,
                "Justification": justification
            })

    if not results:
        st.info("Aucune correspondance pertinente trouvée.")
    else:
        result_df = pd.DataFrame(results).sort_values(
            by="Niveau de pertinence",
            ascending=False
        )

        st.subheader("📊 Résultats de la catégorisation")
        st.dataframe(result_df, use_container_width=True)

# ==============================
# 9. Footer
# ==============================

st.markdown("---")
st.caption("Prototype IA – Analyse et catégorisation des exigences de sécurité")


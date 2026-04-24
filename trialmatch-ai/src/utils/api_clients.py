"""
TrialMatch AI — Government API Clients
Real HTTP calls to ClinicalTrials.gov v2, OpenFDA, and RxNorm.
All public, free, no auth required (OpenFDA key optional for higher rate limits).
"""
import requests
import json
from typing import List, Dict, Optional


class ClinicalTrialsClient:
    """ClinicalTrials.gov v2 API — search and retrieve trial data."""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    
    def search(self, condition: str, max_results: int = 20, 
               phases: List[str] = None, status: str = "RECRUITING") -> List[Dict]:
        """
        Search for trials by condition.
        Returns list of trial dicts with nct_id, title, phase, eligibility, etc.
        """
        params = {
            "query.cond": condition,
            "filter.overallStatus": status,
            "pageSize": min(max_results, 100),
            "fields": "NCTId,BriefTitle,OfficialTitle,OverallStatus,Phase,EligibilityCriteria,BriefSummary,Condition,InterventionName",
        }
        if phases:
            phase_map = {"Phase 1": "PHASE1", "Phase 2": "PHASE2", "Phase 3": "PHASE3", "Phase 4": "PHASE4"}
            mapped = [phase_map.get(p, p) for p in phases]
            params["filter.phase"] = "|".join(mapped)
        
        try:
            resp = requests.get(f"{self.BASE_URL}/studies", params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            trials = []
            for study in data.get("studies", []):
                proto = study.get("protocolSection", {})
                ident = proto.get("identificationModule", {})
                status_mod = proto.get("statusModule", {})
                design = proto.get("designModule", {})
                elig = proto.get("eligibilityModule", {})
                desc = proto.get("descriptionModule", {})
                
                trials.append({
                    "nct_id": ident.get("nctId", ""),
                    "title": ident.get("briefTitle", ident.get("officialTitle", "")),
                    "status": status_mod.get("overallStatus", ""),
                    "phase": ", ".join(design.get("phases", [])) if design.get("phases") else "N/A",
                    "eligibility_criteria": elig.get("eligibilityCriteria", ""),
                    "summary": desc.get("briefSummary", ""),
                    "conditions": proto.get("conditionsModule", {}).get("conditions", []),
                })
            
            return trials
        except requests.RequestException as e:
            return [{"error": str(e), "nct_id": "ERROR", "title": f"API Error: {e}"}]
    
    def get_study(self, nct_id: str) -> Optional[Dict]:
        """Get a single study by NCT ID."""
        try:
            resp = requests.get(f"{self.BASE_URL}/studies/{nct_id}", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except:
            return None


class OpenFDAClient:
    """OpenFDA Drug Label API — drug interactions and label data."""
    
    BASE_URL = "https://api.fda.gov/drug"
    
    def search_drug_label(self, drug_name: str) -> Optional[Dict]:
        """Search for drug label info including interactions and warnings."""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/label.json",
                params={"search": f'openfda.generic_name:"{drug_name}"', "limit": 1},
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                label = results[0]
                return {
                    "drug_name": drug_name,
                    "drug_interactions": label.get("drug_interactions", [""]),
                    "warnings": label.get("warnings", [""]),
                    "contraindications": label.get("contraindications", [""]),
                    "brand_name": label.get("openfda", {}).get("brand_name", [""]),
                }
            return None
        except:
            return None
    
    def check_interactions(self, medications: List[str]) -> List[Dict]:
        """Check for drug interactions across a list of medications."""
        interactions = []
        cyp3a4_inhibitors = ["ketoconazole", "itraconazole", "clarithromycin", "ritonavir", "nefazodone", "cobicistat"]
        cyp3a4_inducers = ["rifampin", "phenytoin", "carbamazepine", "St. John's Wort"]
        
        for med in medications:
            med_lower = med.lower()
            
            # Check CYP3A4 interactions
            if med_lower in cyp3a4_inhibitors:
                interactions.append({
                    "drug": med,
                    "type": "CYP3A4_inhibitor",
                    "severity": "HIGH",
                    "detail": f"{med} is a strong CYP3A4 inhibitor — may increase plasma levels of CYP3A4 substrates",
                })
            elif med_lower in cyp3a4_inducers:
                interactions.append({
                    "drug": med,
                    "type": "CYP3A4_inducer", 
                    "severity": "HIGH",
                    "detail": f"{med} is a strong CYP3A4 inducer — may decrease efficacy of CYP3A4 substrates",
                })
            
            # Try OpenFDA label lookup
            label = self.search_drug_label(med)
            if label and label.get("drug_interactions"):
                interaction_text = label["drug_interactions"][0][:200] if label["drug_interactions"] else ""
                if interaction_text:
                    interactions.append({
                        "drug": med,
                        "type": "label_interaction",
                        "severity": "INFO",
                        "detail": interaction_text,
                    })
        
        return interactions


class RxNormClient:
    """RxNorm API — drug name normalization."""
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    def normalize(self, drug_name: str) -> Optional[Dict]:
        """Normalize a drug name to its RxNorm concept."""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/rxcui.json",
                params={"name": drug_name, "search": 2},
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            ids = data.get("idGroup", {}).get("rxnormId", [])
            if ids:
                return {"input": drug_name, "rxcui": ids[0], "normalized": True}
            return {"input": drug_name, "rxcui": None, "normalized": False}
        except:
            return {"input": drug_name, "rxcui": None, "normalized": False}
    
    def get_drug_info(self, rxcui: str) -> Optional[Dict]:
        """Get drug properties by RxCUI."""
        try:
            resp = requests.get(f"{self.BASE_URL}/rxcui/{rxcui}/properties.json", timeout=8)
            resp.raise_for_status()
            props = resp.json().get("properties", {})
            return {"rxcui": rxcui, "name": props.get("name", ""), "synonym": props.get("synonym", "")}
        except:
            return None

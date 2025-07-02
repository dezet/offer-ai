from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime

# --- Intermediate Extraction Models ---

class ExtractedPage(BaseModel):
    page_number: int
    content: str

class ExtractedFile(BaseModel):
    filename: str
    extraction_method: Literal['ocr', 'text']
    pages: List[ExtractedPage]

# --- Target Offer Template Models (with Polish comments for AI) ---

class FormInfo(BaseModel):
    description: str  # Opis sekcji
    documentTitle: str  # Klucz: Tytuł dokumentu
    documentVersion: str  # Klucz: Wersja dokumentu
    projectCaretakersDPI: str  # Klucz: Opiekunowie projektu z ramienia DPI
    projectCaretakersRealization: str  # Klucz: Opiekunowie projektu z ramienia Realizacji
    updateDates: List[str]  # Klucz: Daty aktualizacji
    version: int  # Klucz: Wersja
    projectContract: str  # Klucz: Kontrakt na projekt
    investor: str  # Klucz: Inwestor
    offerMode: str  # Klucz: Tryb oferty
    requiredCompletionDate: str  # Klucz: Wymagany termin realizacji

class GeneralData(BaseModel):
    description: str  # Opis sekcji
    connectionPower: str  # Klucz: Moc przyłączeniowa
    maxPowerNcRfg: str  # Klucz: Moc maksymalna NcRfG
    activePowerLimitPcc: str  # Klucz: Ograniczenie mocy czynnej w PCC
    connectionVoltage: str  # Klucz: Napięcie przyłączenia
    shortCircuitCurrentPcc: str  # Klucz: Prąd zwarciowy w PCC
    otherImportantInfo: str  # Klucz: Inne ważne informacje

class Connection(BaseModel):
    description: str  # Opis sekcji
    connectionLength: str  # Klucz: Długość przyłącza
    cableSlackGuideline: str  # Klucz: Wytyczna dot. zapasu kabla
    shortCircuitStrengthRequirements: str  # Klucz: Wymagania wytrzymałości zwarciowej
    conductorMaterial: str  # Klucz: Materiał żyły roboczej
    allowConductorGrading: str  # Klucz: Zgoda na stopniowanie żył roboczych
    allowReturnConductorGrading: str  # Klucz: Zgoda na stopniowanie żył powrotnych
    otherSpecialRequirements: str  # Klucz: Inne wymagania szczególne
    allowedDailyLoadFactor: str  # Klucz: Dopuszczalny współczynnik obciążenia dobowego
    maxLayingDepth: str  # Klucz: Maksymalna głębokość ułożenia
    concreteBentoniteRequirement: str  # Klucz: Wymóg dot. betonu/bentonitu
    otherObjectsLimitingLoad: str  # Klucz: Inne obiekty ograniczające obciążalność
    otherConnectionNotes: str  # Klucz: Inne uwagi dot. przyłącza

class Gpo(BaseModel):
    description: str  # Opis sekcji
    stationLayoutAndConditions: str  # Klucz: Układ i uwarunkowania stacji
    compensationType: str  # Klucz: Rodzaj kompensacji
    structureSolutions: str  # Klucz: Rozwiązania konstrukcyjne
    switchgearType: str  # Klucz: Typ rozdzielnicy
    otherGpoNotes: str  # Klucz: Inne uwagi dot. GPO

class PowerTransformer(BaseModel):
    description: str  # Opis sekcji
    minPower: str  # Klucz: Moc minimalna
    requiredShortCircuitVoltage: str  # Klucz: Wymagane napięcie zwarcia
    requiredHvMvRatio: str  # Klucz: Wymagana przekładnia GN/SN
    minTapChangerRange: str  # Klucz: Minimalny zakres przełącznika zaczepów
    tapChangerType: str  # Klucz: Typ przełącznika zaczepów
    insulationLevelHvMv: str  # Klucz: Poziom izolacji GN/SN
    maxNoLoadLoadLosses: str  # Klucz: Maksymalne straty jałowe i obciążeniowe
    coolingType: str  # Klucz: Rodzaj chłodzenia
    bushingType: str  # Klucz: Typ izolatorów przepustowych
    noLoadCurrent: str  # Klucz: Prąd stanu jałowego
    otherTransformerNotes: str  # Klucz: Inne uwagi dot. transformatora

class MvSwitchgear(BaseModel):
    description: str  # Opis sekcji
    operatingMaxVoltage: str  # Klucz: Napięcie robocze maksymalne
    shortCircuitStrengthAndTime: str  # Klucz: Wytrzymałość zwarciowa i czas
    peakWithstandCurrent: str  # Klucz: Prąd znamionowy szczytowy wytrzymywany
    busbarContinuousCurrent: str  # Klucz: Prąd znamionowy ciągły szyn zbiorczych
    requiredBayTypesAndCount: str  # Klucz: Wymagane typy i liczba pól
    requiredInsulationLevel: str  # Klucz: Wymagany poziom izolacji
    recommendedSolutions: str  # Klucz: Rekomendowane rozwiązania
    otherSwitchgearNotes: str  # Klucz: Inne uwagi dot. rozdzielnicy

class MvTopology(BaseModel):
    description: str  # Opis sekcji
    minConductorCrossSection: str  # Klucz: Minimalny przekrój żyły roboczej
    maxConductorCrossSection: str  # Klucz: Maksymalny przekrój żyły roboczej
    allowedDailyLoadFactorMv: str  # Klucz: Dopuszczalny współczynnik obciążenia dobowego SN
    specialShortCircuitRequirements: str  # Klucz: Specjalne wymagania dot. zwarć
    conductorMaterialMv: str  # Klucz: Materiał żyły roboczej SN
    minCableLayingDepth: str  # Klucz: Minimalna głębokość ułożenia kabli
    cableSlackGuidelineMv: str  # Klucz: Wytyczna dot. zapasu kabla SN
    maxVoltageDropPowerLoss: str  # Klucz: Maksymalny spadek napięcia/straty mocy
    neutralPointGroundingMethod: str  # Klucz: Sposób pracy punktu neutralnego
    returnConductorShortCircuitStrength: str  # Klucz: Wytrzymałość zwarciowa żyły powrotnej
    otherTopologyNotes: str  # Klucz: Inne uwagi dot. topologii SN

class PvGeneration(BaseModel):
    description: str  # Opis sekcji
    inverterTypeAndCount: str  # Klucz: Typ i liczba falowników
    panelTypeAndCount: str  # Klucz: Typ i liczba paneli
    deviationsFromConditions: str  # Klucz: Odstępstwa od warunków
    pvStationTypeCountAndPower: str  # Klucz: Typ, liczba i moc stacji PV
    topologyDrawingFile: str  # Klucz: Plik z rysunkiem topologii
    allowNighttimeReactivePower: str  # Klucz: Zgoda na nocną generację mocy biernej
    allowReactivePowerRegulation: str  # Klucz: Zgoda na regulację mocy biernej
    pvsystSimulationParameters: str  # Klucz: Parametry symulacji PVsyst
    constructionType: str  # Klucz: Rodzaj konstrukcji
    preferredTableDimensions: str  # Klucz: Preferowane wymiary stołów
    otherRequirements: str  # Klucz: Inne wymagania
    projectLayoutMapFile: str  # Klucz: Plik z mapą layoutu projektu
    preferredPanelWiring: str  # Klucz: Preferowany sposób łączenia paneli
    permissibleInstallationParametersDS: str  # Klucz: Dopuszczalne parametry zabudowy DS
    permissibleInstallationParametersWZ: str  # Klucz: Dopuszczalne parametry zabudowy WZ
    preferredDcAcRatio: str  # Klucz: Preferowany współczynnik DC/AC
    otherPvGenerationNotes: str  # Klucz: Inne uwagi dot. generacji PV

class WindGeneration(BaseModel):
    description: str  # Opis sekcji
    turbineTypeAndCount: str  # Klucz: Typ i liczba turbin
    fwTopologyDrawingFile: str  # Klucz: Plik z rysunkiem topologii FW
    turbineReactivePowerCapability: str  # Klucz: Zdolność generacji mocy biernej turbin
    reactivePowerLimitations: str  # Klucz: Ograniczenia w generacji mocy biernej
    activePowerCurtailment: str  # Klucz: Ograniczenie mocy czynnej
    turbineTransformerData: str  # Klucz: Dane transformatora turbinowego
    maxMvCrossSectionToTurbine: str  # Klucz: Maksymalny przekrój SN do turbiny
    otherWindGenerationNotes: str  # Klucz: Inne uwagi dot. generacji FW

class OtherAtypicalRequirements(BaseModel):
    description: str  # Opis sekcji
    preferredManufacturers: str  # Klucz: Preferowani producenci
    otherNotes: str  # Klucz: Inne uwagi

class InternalMvCable(BaseModel):
    from_loc: str = Field(..., alias='from')  # Kolumna w tabeli: od
    to: str  # Kolumna w tabeli: do
    routeLengthKm: float  # Kolumna w tabeli: [km]
    inverterCount: int  # Kolumna w tabeli: Liczba falowników na stację
    powerMva: float  # Kolumna w tabeli: Moc (MVA)
    currentA: float  # Kolumna w tabeli: A
    conductorCrossSectionMm2: int  # Kolumna w tabeli: mm2 (Srobocza)
    returnCrossSectionMm2: int  # Kolumna w tabeli: mm2 (Spowrt)
    coresPerPhase: int  # Kolumna w tabeli: szt.

class RequiredScope(BaseModel):
    description: str  # Opis sekcji
    tableLengthRequest: str  # Klucz: Wniosek dot. długości stołów
    mvLvStationQuantityCheck: str  # Klucz: Sprawdzenie ilości stacji SN/nn
    inverterQuantityCheck: str  # Klucz: Sprawdzenie ilości falowników
    internalMvLineCheck: str  # Klucz: Sprawdzenie wewnętrznych linii SN
    internalMvCableNotes: str  # Klucz: Uwagi do kabli SN wewnętrznych
    internalMvCables: List[InternalMvCable]  # Tabela: Kable SN wewnętrzne
    dcCableQuantityAndCrossSectionRequest: str  # Klucz: Wniosek o ilość i przekroje kabli DC
    acCableQuantityAndCrossSectionRequest: str  # Klucz: Wniosek o ilość i przekroje kabli AC
    cableJointsConceptCheck: str  # Klucz: Sprawdzenie koncepcji muf kablowych
    powerEvacuationMvLineCheck: str  # Klucz: Sprawdzenie linii SN wyprowadzenia mocy
    newConceptRequest: str  # Klucz: Wniosek o nową koncepcję
    tableAndStringLengthForNewPanelsRequest: str  # Klucz: Wniosek o długość stołów i stringów dla nowych paneli
    dcCableQuantityAndCrossSectionRequestNew: str  # Klucz: Wniosek o ilość i przekroje kabli DC (nowe)
    acCableQuantityAndCrossSectionRequestNew: str  # Klucz: Wniosek o ilość i przekroje kabli AC (nowe)
    mvLvStationQuantityCheckNew: str  # Klucz: Sprawdzenie ilości stacji SN/nn (nowe)
    inverterQuantityCheckNew: str  # Klucz: Sprawdzenie ilości falowników (nowe)
    reactivePowerRegulationNote: str  # Klucz: Uwaga dot. regulacji mocy biernej

class Selections(BaseModel):
    description: str  # Opis sekcji
    selectionA: str  # Klucz: Dobór A
    selectionB: str  # Klucz: Dobór B

class OfferTemplate(BaseModel):
    formInfo: FormInfo
    generalData: GeneralData
    connection: Connection
    gpo: Gpo
    powerTransformer: PowerTransformer
    mvSwitchgear: MvSwitchgear
    mvTopology: MvTopology
    pvGeneration: PvGeneration
    windGeneration: WindGeneration
    otherAtypicalRequirements: OtherAtypicalRequirements
    requiredScope: RequiredScope
    selections: Selections

# --- Final Result Model ---

class LLMRequest(BaseModel):
    prompt_sent: str
    llm_provider: str
    llm_model: str
    source_filenames: List[str]

class FinalResult(BaseModel):
    request_details: LLMRequest
    filled_offer: OfferTemplate
    llm_response_raw: Union[dict, str]
    processing_timestamp: datetime
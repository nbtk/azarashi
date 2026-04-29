#pragma once
// AUTO-GENERATED from azarashi 0.15.1 — do not edit
// Source module : qzss_dcx_camf_b4_lower_level_fields_tables
// Variable      : qzss_dcx_camf_d30_nuclear_event_scale
// Entries       : 9
// Strategy      : switch

#include <cstdint>

namespace azaraC {
namespace def {

inline constexpr const char* qzss_dcx_camf_d30_nuclear_event_scale_lookup(uint8_t id) {
    switch (id) {
        case 0: return "Unknown";
        case 1: return "Level 0/7. Deviation. No safety significance";
        case 2: return "Level 1/7. Anomaly. Overexposure in excess of statutory annual limits. Minor problems with safety components with significant defence-in-depth remaining. Low activity lost or stolen radioactive source, device, or transport package.";
        case 3: return "Level 2/7. Incident. Impact on people and environment: Exposure of the public in excess of 10 mSv. Exposure of workers in excess of the statutory annual limits. Impact on radiological barriers and control: Radiation levels in an operating area of more than 50 mSv/h. Significant contamination within the facility into an area not expected by design. Possible cause: Significant failures in safety provisions but with no actual consequences. Found highly radioactive sealed orphan source, device or transport package with safety provisions intact. Inadequate packaging of a highly radioactive sealed source.";
        case 4: return "Level 3/7. Serious incident. Impact on people and environment: Exposure in excess of ten times the statutory annual limit for workers. Non-lethal deterministic health effect (e.g., burns) from radiation. Impact on radiological barriers and control: Exposure rates of more than 1 Sv/h in an operating area. Severe contamination in an area not expected by design, with a low probability of significant public exposure. Possible cause: Near-accident at a nuclear power plant with no safety provisions remaining. Lost or stolen highly radioactive sealed source. Misdelivered highly radioactive sealed source without adequate procedures in place to handle it.";
        case 5: return "Level 4/7. Accident with local consequences. Impact on people and environment: Minor release of radioactive material unlikely to result in implementation of planned countermeasures other than local food controls. Impact on radiological barriers and control: Release of significant quantities of radioactive material within an installation with a high probability of significant public exposure.";
        case 6: return "Level 5/7. Accident with wider consequences. Impact on people and environment: Limited release of radioactive material likely to require implementation of some planned countermeasures. Major health impact from radiation is likely. Impact on radiological barriers and control: Severe damage to reactor core. Release of large quantities of radioactive material within an installation with a high probability of significant public exposure. This could arise from a major criticality accident or fire.";
        case 7: return "Level 6/7. Serious accident. Impact on people and environment: Significant release of radioactive material likely to require implementation of planned countermeasures.";
        case 8: return "Level 7/7. Major accident. Impact on people and environment: Major release of radioactive material with widespread health and environmental effects requiring implementation of planned and extended countermeasures.";
        default: return nullptr;
    }
}

} // namespace def
} // namespace azaraC

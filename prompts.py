"""Historically-researched prompts for the timeport 360 panoramas.

Every prompt opens with the equirectangular LoRA's trigger phrase and closes with a
photographic-realism clause.

A note on exclusions: FLUX.1-dev is guidance-distilled and `fal-ai/flux-lora` exposes
no `negative_prompt` field, so exclusions cannot be passed to the model. They are
handled two ways instead -- by describing the period-correct thing positively and
precisely (diffusion models follow assertion far better than negation), and by the
`exclude` list below, which is the manual QA checklist used when curating candidates.
Each entry says what must NOT appear and why it is period-wrong.
"""

TRIGGER = "equirectangular 360 degree panorama"

# Deliberately does NOT say "documentary photography". First Manchester run showed the
# model reads that as "a photo taken today", and returned a preserved heritage town full
# of tourists in modern coats. Describing the film/plate stock per era instead anchors
# the image in its period without inviting a present-day crowd.
REALISM = (
    "photorealistic, natural colour, fine detail, correct perspective, sharp focus, "
    "high dynamic range, cinematic historical reconstruction, feature film production design"
)

# With no negative_prompt available, the strongest lever is asserting the correct thing
# rather than naming the wrong one. These carry the exclusions that actually failed.
NO_MODERNS = (
    "Every single person visible is dressed in strictly period clothing appropriate to the "
    "year; there are no modern people, no tourists, no contemporary clothing, no visitors "
    "and no signage in modern typefaces anywhere in the scene."
)

ERAS = {
    "manchester": {
        "name": "Manchester",
        "year": 1750,
        "place": "Market Place",
        "asset": "manchester-1750.jpg",
        # Chrome: copperplate engraving -- the only visual record of 1750 Manchester
        "accent": "#E8E0CC",
        "medium": "engraving",
        "heading": 42,
        "prompt": (
            f"{TRIGGER}, street-level view in the Market Place of Manchester England in 1750, "
            "a prosperous Georgian market town of seventeen thousand people, three decades before "
            "any factory was built there. "
            "Timber-framed buildings with weathered silver-grey oak framing and cream limewashed "
            "infill panels, jettied overhanging upper floors, three storeys with gabled attics. "
            "Beside them newer early-Georgian houses in warm orange-red brick with small-paned "
            "six-over-six sash windows set in thick white-painted glazing bars. "
            "The low embattled tower of the Collegiate Church in eroded dusky red-brown sandstone "
            "rises just above the rooftops, crowded close by houses on every side. "
            "A street of rounded river cobbles, uneven and bulging, with an open kennel gutter "
            "running down the middle. Painted pictorial shop signs hang on wrought-iron brackets "
            "over the street. Open-air market stalls of wooden trestles, boards on barrels and "
            "canvas awnings, wicker baskets of produce. "
            "A packhorse train with wicker panniers, small two-wheeled horse carts, driven geese. "
            "Men in tricorne hats, knee breeches, long waistcoats to mid-thigh and coarse linen "
            "shirts; women in printed bedgowns, linen aprons, white linen caps and scarlet hooded "
            "wool cloaks. Everything patched, faded, dirty at the hem. "
            "Flat overcast north-west England sky, a high luminous pearl-grey stratus deck, no "
            "visible sun and no hard shadows, soft omnidirectional light. "
            "Thin domestic coal smoke drifting from many small chimney stacks and hanging as a "
            "low haze at roof level. Wet cobbles after rain, standing puddles in the ruts. "
            "Open fields and hedgerows visible where the town ends abruptly. "
            # corrections after run 1: modern crowd, kerbs/pavements, plate glass
            "The ground is rough uneven cobblestone and bare packed earth from wall to wall, "
            "with no kerbstones, no flagstone pavement, no road markings and no tarmac. "
            "All windows are small leaded casements and small panes of wavy greenish glass in "
            "thick glazing bars, never large sheets of clear glass. "
            f"{NO_MODERNS} "
            f"{REALISM}"
        ),
        "exclude": [
            "factory chimneys or smokestacks (first Manchester mill 1782)",
            "cotton mills, engine houses, multi-storey warehouses (1780s+)",
            "canals (Bridgewater reached Manchester 1765)",
            "railways (1830)",
            "gas or oil street lamps (streets were unlit; gas 1807)",
            "kerbs, flagged pavements, tarmac (Improvement Acts 1775+)",
            "chimney pots (19th century)",
            "top hats (1790s+), trousers (1800s+), poke bonnets (1800s+)",
            "plate glass or large-paned shopfronts, flat fascia signs (post-1762)",
            "Victorian Gothic architecture, spires (no tall spire until 1756)",
        ],
    },
    "times-square": {
        "name": "Times Square",
        "year": 1910,
        "place": "Broadway at Seventh Avenue",
        "asset": "times-square-1910.jpg",
        # Chrome: silver-gelatin glass plate -- the Great White Way in white bulbs
        "accent": "#FFF6E2",
        "medium": "silver",
        "heading": 198,
        "prompt": (
            f"{TRIGGER}, street-level view at the bowtie of Times Square New York City in 1910, "
            "where Broadway crosses Seventh Avenue. "
            "The Times Tower stands as an ornate twenty-five storey Italian campanile clad in "
            "cream limestone and terracotta, with heavy bracketed cornices, arcaded windows and "
            "turret-like projecting corner piers, a flagpole at its crown. "
            "Around it a low ragged cornice line of four to twelve storey masonry buildings under "
            "a wide open sky, with large green oxidised-copper mansard roofs and dormers on the "
            "Hotel Astor and the Knickerbocker Hotel. "
            "Skeletal steel and timber billboard scaffolds stand on the rooftops and blank party "
            "walls, their designs picked out in thousands of individual clear incandescent bulbs, "
            "the guy wires, catwalks, ladders and unpainted backs of the frames plainly visible. "
            "Free-standing cast-iron and wire-glass subway kiosks with domed roofs of overlapping "
            "leaf-shaped shingles, painted dark green, stand on the sidewalk. "
            "Sheet-asphalt roadway with granite setts laid in the strip around the streetcar "
            "rails, a narrow conduit slot between them, and a clean empty sky with no wires "
            "crossing it. Ornamental fluted cast-iron lamp posts carrying arc lamps. "
            "Wooden streetcars with clerestory monitor roofs and lifeguard fenders. "
            "Open brass-era touring cars with polished brass radiator shells, brass headlamp "
            "rims, acetylene lamps and wooden artillery wheels with pale narrow tyres; hansom "
            "cabs, four-wheel broughams, and heavy horse-drawn delivery drays. "
            "Men in dark sack suits with stiff white collars, wearing derby hats and straw "
            "boaters; women in enormous wide-brimmed hats piled with ostrich plumes and "
            "artificial flowers, in narrow high-waisted skirts sweeping the ground. "
            "Every head is covered. "
            "Wooden water tanks on steel legs on the rooftops, striped canvas awnings over the "
            "ground-floor shops, painted theatre billboards. "
            "Hazy coal-smoke daylight, desaturated grey-brown palette, soot-darkened stone. "
            "The roadway is bare asphalt and granite sett with no painted markings of any kind. "
            "Every illuminated sign is built from separate round incandescent light bulbs "
            "mounted on an open frame, never a continuous glowing tube or a smooth panel. "
            f"{NO_MODERNS} "
            f"{REALISM}, large format glass plate photograph"
        ),
        "exclude": [
            "neon or any glowing tube signage (first Times Square neon 1924)",
            "the news ticker zipper (1928)",
            "LED screens, video billboards, jumbotrons",
            "Art Deco buildings or setback ziggurat towers (1916 zoning onward)",
            "the reskinned blank One Times Square (1963-66)",
            "Paramount Building (1926), Woolworth (1913), Empire State (1931)",
            "overhead trolley wires, trolley poles, span wires (conduit system!)",
            "elevated railway structure over Broadway",
            "traffic lights (1920), lane markings, crosswalk stripes",
            "modern yellow taxicabs, closed-body cars with fixed steel roofs",
            "bare heads, bobbed hair, short skirts",
        ],
    },
    "alexandria": {
        "name": "Alexandria",
        "year": 1970,
        "place": "the Corniche",
        "asset": "alexandria-1970.jpg",
        # Chrome: Kodachrome slide film -- warm, faded, fine-grained
        "accent": "#E8A33D",
        "medium": "kodachrome",
        "heading": 310,
        "prompt": (
            f"{TRIGGER}, street-level view on the Corniche of Alexandria Egypt in 1970. "
            "A narrow seafront road only about eight metres wide, one lane each way, running "
            "beside a low continuous concrete sea parapet with a rounded coping; men sit along "
            "the parapet facing the water. The crescent of the Eastern Harbour curves away into "
            "the haze, with fishing boats moored inside it and a wide sandy beach below the wall. "
            "A near-continuous wall of five to eight storey apartment blocks lines the road: "
            "faded Italianate and Belle Epoque facades in salt-bleached sand-ochre, cream, pale "
            "buttery yellow and dusty rose stucco, mixed with plain grey-white 1960s concrete "
            "blocks with horizontal balcony bands. The render is crazed and flaking in map-like "
            "patches, rust bleeds in streaks from the balcony ironwork, black damp stains sit "
            "under the sills. Green and brown louvered timber shutters, many slats missing, "
            "laundry strung across the balconies, television aerials cluttering every roofline. "
            "A blue and cream tram runs on rails embedded flush in the asphalt under a single "
            "overhead wire carried on tapered steel poles, packed with passengers, men riding on "
            "the running board. Peugeot 404 and Nasr 1100 saloons, black-and-yellow taxis, "
            "battered 1950s American sedans with mismatched panels, a donkey cart stacked with "
            "vegetables. "
            "Men in striped galabeyas and open-necked short-sleeved shirts, thick moustaches and "
            "heavy sideburns; bare-headed women in knee-length A-line dresses with hair set in "
            "bouffants; older women wrapped head to ankle in black milaya laff over a print house "
            "dress. Hand-painted Arabic shop fascia boards in bold naskh lettering above the "
            "shopfronts. "
            "Far along the spit the pale weathered limestone of the Qaitbay citadel sits low on "
            "the water, unrestored and faded almost to the colour of the sky. "
            "Humid Mediterranean marine haze, strong aerial perspective washing out the distance, "
            "warm west-raking late afternoon light on the stucco, the sea going silver-grey. "
            "The younger women are bare-headed with their hair uncovered and visible, in the "
            "secular Western dress ordinary in Egyptian cities in 1970; the only covered heads "
            "are older working women in the loose black milaya laff wrap. "
            "The seafront road stays narrow, a single lane in each direction, never a wide "
            "modern highway. Every building along it is low, between five and eight storeys. "
            f"{NO_MODERNS} "
            f"{REALISM}, Kodachrome colour slide film, warm faded palette, fine grain"
        ),
        "exclude": [
            "hijab, headscarf worn as hijab, niqab, abaya (urban veiling post-dates 1970)",
            "Bibliotheca Alexandrina (opened 2002)",
            "Stanley Bridge (2001)",
            "the widened multi-lane Corniche (2001) -- must stay narrow",
            "modern high-rise towers, glass curtain walls",
            "satellite dishes (1990s), split air-conditioning units",
            "Coca-Cola signage (Arab League boycott, banned in Egypt 1968-late 70s; use Pepsi)",
            "Lada / Zhiguli cars (Egyptian assembly from 2003)",
            "microbuses, tuk-tuks, modern cars, all-yellow metered taxis (2006)",
            "a visibly European tourist crowd (the cosmopolitan community left by 1962)",
        ],
    },
}

ORDER = ["manchester", "times-square", "alexandria"]

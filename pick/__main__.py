from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio
import cairo, math, json, os, codecs, time

# Colour names list from http://chir.ag/projects/ntc/ntc.js, for which many thanks
# Used under CC-BY 2.5

COLOUR_NAMES = [(0, 0, 0, 'Black'), (0, 0, 128, 'Navy Blue'), (0, 0, 200,
'Dark Blue'), (0, 0, 255, 'Blue'), (0, 7, 65, 'Stratos'), (0, 27, 28,
'Swamp'), (0, 35, 135, 'Resolution Blue'), (0, 41, 0, 'Deep Fir'), (0, 46, 32,
'Burnham'), (0, 47, 167, 'International Klein Blue'), (0, 49, 83, 'Prussian Blue'), 
(0, 51, 102, 'Midnight Blue'), (0, 51, 153, 'Smalt'), (0, 53, 50,
'Deep Teal'), (0, 62, 64, 'Cyprus'), (0, 70, 32, 'Kaitoke Green'), (0, 71,
171, 'Cobalt'), (0, 72, 22, 'Crusoe'), (0, 73, 80, 'Sherpa Blue'), (0, 86,
167, 'Endeavour'), (0, 88, 26, 'Camarone'), (0, 102, 204, 'Science Blue'), (0,
102, 255, 'Blue Ribbon'), (0, 117, 94, 'Tropical Rain Forest'), (0, 118, 163,
'Allports'), (0, 123, 167, 'Deep Cerulean'), (0, 126, 199, 'Lochmara'), (0,
127, 255, 'Azure Radiance'), (0, 128, 128, 'Teal'), (0, 149, 182, 'Bondi Blue'), 
(0, 157, 196, 'Pacific Blue'), (0, 166, 147, 'Persian Green'), (0,
168, 107, 'Jade'), (0, 204, 153, 'Caribbean Green'), (0, 204, 204, "Robin's Egg Blue"), 
(0, 255, 0, 'Green'), (0, 255, 127, 'Spring Green'), (0, 255, 255,
'Cyan / Aqua'), (1, 13, 26, 'Blue Charcoal'), (1, 22, 53, 'Midnight'), (1, 29,
19, 'Holly'), (1, 39, 49, 'Daintree'), (1, 54, 28, 'Cardin Green'), (1, 55,
26, 'County Green'), (1, 62, 98, 'Astronaut Blue'), (1, 63, 106, 'Regal Blue'), 
(1, 75, 67, 'Aqua Deep'), (1, 94, 133, 'Orient'), (1, 97, 98, 'Blue Stone'), 
(1, 109, 57, 'Fun Green'), (1, 121, 111, 'Pine Green'), (1, 121, 135,
'Blue Lagoon'), (1, 130, 107, 'Deep Sea'), (1, 163, 104, 'Green Haze'), (2,
45, 21, 'English Holly'), (2, 64, 44, 'Sherwood Green'), (2, 71, 142,
'Congress Blue'), (2, 78, 70, 'Evening Sea'), (2, 99, 149, 'Bahama Blue'), (2,
134, 111, 'Observatory'), (2, 164, 211, 'Cerulean'), (3, 22, 60, 'Tangaroa'),
(3, 43, 82, 'Green Vogue'), (3, 106, 110, 'Mosque'), (4, 16, 4, 'Midnight Moss'), 
(4, 19, 34, 'Black Pearl'), (4, 46, 76, 'Blue Whale'), (4, 64, 34,
'Zuccini'), (4, 66, 89, 'Teal Blue'), (5, 16, 64, 'Deep Cove'), (5, 22, 87,
'Gulf Blue'), (5, 89, 137, 'Venice Blue'), (5, 111, 87, 'Watercourse'), (6,
42, 120, 'Catalina Blue'), (6, 53, 55, 'Tiber'), (6, 155, 129, 'Gossamer'),
(6, 161, 137, 'Niagara'), (7, 58, 80, 'Tarawera'), (8, 1, 16, 'Jaguar'), (8,
25, 16, 'Black Bean'), (8, 37, 103, 'Deep Sapphire'), (8, 131, 112, 'Elf Green'), 
(8, 232, 222, 'Bright Turquoise'), (9, 34, 86, 'Downriver'), (9, 35,
15, 'Palm Green'), (9, 37, 93, 'Madison'), (9, 54, 36, 'Bottle Green'), (9,
88, 89, 'Deep Sea Green'), (9, 127, 75, 'Salem'), (10, 0, 28, 'Black Russian'), 
(10, 72, 13, 'Dark Fern'), (10, 105, 6, 'Japanese Laurel'), (10,
111, 117, 'Atoll'), (11, 11, 11, 'Cod Gray'), (11, 15, 8, 'Marshland'), (11,
17, 7, 'Gordons Green'), (11, 19, 4, 'Black Forest'), (11, 98, 7, 'San Felix'), 
(11, 218, 81, 'Malachite'), (12, 11, 29, 'Ebony'), (12, 13, 15,
'Woodsmoke'), (12, 25, 17, 'Racing Green'), (12, 122, 121, 'Surfie Green'),
(12, 137, 144, 'Blue Chill'), (13, 3, 50, 'Black Rock'), (13, 17, 23,
'Bunker'), (13, 28, 25, 'Aztec'), (13, 46, 28, 'Bush'), (14, 14, 24,
'Cinder'), (14, 42, 48, 'Firefly'), (15, 45, 158, 'Torea Bay'), (16, 18, 29,
'Vulcan'), (16, 20, 5, 'Green Waterloo'), (16, 88, 82, 'Eden'), (17, 12, 108,
'Arapawa'), (18, 10, 143, 'Ultramarine'), (18, 52, 71, 'Elephant'), (18, 107,
64, 'Jewel'), (19, 0, 0, 'Diesel'), (19, 10, 6, 'Asphalt'), (19, 38, 77, 'Blue Zodiac'), 
(19, 79, 25, 'Parsley'), (20, 6, 0, 'Nero'), (20, 80, 170, 'Tory Blue'), 
(21, 31, 76, 'Bunting'), (21, 96, 189, 'Denim'), (21, 115, 107,
'Genoa'), (22, 25, 40, 'Mirage'), (22, 29, 16, 'Hunter Green'), (22, 42, 64,
'Big Stone'), (22, 50, 34, 'Celtic'), (22, 50, 44, 'Timber Green'), (22, 53,
49, 'Gable Green'), (23, 31, 4, 'Pine Tree'), (23, 85, 121, 'Chathams Blue'),
(24, 45, 9, 'Deep Forest Green'), (24, 88, 122, 'Blumine'), (25, 51, 14, 'Palm Leaf'), 
(25, 55, 81, 'Nile Blue'), (25, 89, 168, 'Fun Blue'), (26, 26, 104,
'Lucky Point'), (26, 179, 133, 'Mountain Meadow'), (27, 2, 69, 'Tolopea'),
(27, 16, 53, 'Haiti'), (27, 18, 123, 'Deep Koamaru'), (27, 20, 4, 'Acadia'),
(27, 47, 17, 'Seaweed'), (27, 49, 98, 'Biscay'), (27, 101, 157, 'Matisse'),
(28, 18, 8, 'Crowshead'), (28, 30, 19, 'Rangoon Green'), (28, 57, 187,
'Persian Blue'), (28, 64, 46, 'Everglade'), (28, 124, 125, 'Elm'), (29, 97,
66, 'Green Pea'), (30, 15, 4, 'Creole'), (30, 22, 9, 'Karaka'), (30, 23, 8,
'El Paso'), (30, 56, 91, 'Cello'), (30, 67, 60, 'Te Papa Green'), (30, 144,
255, 'Dodger Blue'), (30, 154, 176, 'Eastern Blue'), (31, 18, 15, 'Night Rider'), 
(31, 194, 194, 'Java'), (32, 32, 141, 'Jacksons Purple'), (32, 46,
84, 'Cloud Burst'), (32, 72, 82, 'Blue Dianne'), (33, 26, 14, 'Eternity'),
(34, 8, 120, 'Deep Blue'), (34, 139, 34, 'Forest Green'), (35, 52, 24,
'Mallard'), (36, 10, 64, 'Violet'), (36, 12, 2, 'Kilamanjaro'), (36, 42, 29,
'Log Cabin'), (36, 46, 22, 'Black Olive'), (36, 80, 15, 'Green House'), (37,
22, 7, 'Graphite'), (37, 23, 6, 'Cannon Black'), (37, 31, 79, 'Port Gore'),
(37, 39, 44, 'Shark'), (37, 49, 28, 'Green Kelp'), (37, 150, 209, 'Curious Blue'), 
(38, 3, 104, 'Paua'), (38, 5, 106, 'Paris M'), (38, 17, 5, 'Wood Bark'), 
(38, 20, 20, 'Gondola'), (38, 35, 53, 'Steel Gray'), (38, 40, 59,
'Ebony Clay'), (39, 58, 129, 'Bay of Many'), (39, 80, 75, 'Plantation'), (39,
138, 91, 'Eucalyptus'), (40, 30, 21, 'Oil'), (40, 58, 119, 'Astronaut'), (40,
106, 205, 'Mariner'), (41, 12, 94, 'Violent Violet'), (41, 33, 48,
'Bastille'), (41, 35, 25, 'Zeus'), (41, 41, 55, 'Charade'), (41, 123, 154,
'Jelly Bean'), (41, 171, 135, 'Jungle Green'), (42, 3, 89, 'Cherry Pie'), (42,
20, 14, 'Coffee Bean'), (42, 38, 48, 'Baltic Sea'), (42, 56, 11, 'Turtle Green'), 
(42, 82, 190, 'Cerulean Blue'), (43, 2, 2, 'Sepia Black'), (43, 25,
79, 'Valhalla'), (43, 50, 40, 'Heavy Metal'), (44, 14, 140, 'Blue Gem'), (44,
22, 50, 'Revolver'), (44, 33, 51, 'Bleached Cedar'), (44, 140, 132,
'Lochinvar'), (45, 37, 16, 'Mikado'), (45, 56, 58, 'Outer Space'), (45, 86,
155, 'St Tropaz'), (46, 3, 41, 'Jacaranda'), (46, 25, 5, 'Jacko Bean'), (46,
50, 34, 'Rangitoto'), (46, 63, 98, 'Rhino'), (46, 139, 87, 'Sea Green'), (46,
191, 212, 'Scooter'), (47, 39, 14, 'Onion'), (47, 60, 179, 'Governor Bay'),
(47, 81, 158, 'Sapphire'), (47, 90, 87, 'Spectra'), (47, 97, 104, 'Casal'),
(48, 5, 41, 'Melanzane'), (48, 31, 30, 'Cocoa Brown'), (48, 42, 15,
'Woodrush'), (48, 75, 106, 'San Juan'), (48, 213, 200, 'Turquoise'), (49, 28,
23, 'Eclipse'), (49, 68, 89, 'Pickled Bluewood'), (49, 91, 161, 'Azure'), (49,
114, 141, 'Calypso'), (49, 125, 130, 'Paradiso'), (50, 18, 122, 'Persian Indigo'), 
(50, 41, 58, 'Blackcurrant'), (50, 50, 50, 'Mine Shaft'), (50, 93,
82, 'Stromboli'), (50, 124, 20, 'Bilbao'), (50, 125, 160, 'Astral'), (51, 3,
107, 'Christalle'), (51, 41, 47, 'Thunder'), (51, 204, 153, 'Shamrock'), (52,
21, 21, 'Tamarind'), (53, 0, 54, 'Mardi Gras'), (53, 14, 66, 'Valentino'),
(53, 14, 87, 'Jagger'), (53, 53, 66, 'Tuna'), (53, 78, 140, 'Chambray'), (54,
48, 80, 'Martinique'), (54, 53, 52, 'Tuatara'), (54, 60, 13, 'Waiouru'), (54,
116, 125, 'Ming'), (54, 135, 22, 'La Palma'), (55, 2, 2, 'Chocolate'), (55,
29, 9, 'Clinker'), (55, 41, 14, 'Brown Tumbleweed'), (55, 48, 33, 'Birch'),
(55, 116, 117, 'Oracle'), (56, 4, 116, 'Blue Diamond'), (56, 26, 81, 'Grape'),
(56, 53, 51, 'Dune'), (56, 69, 85, 'Oxford Blue'), (56, 73, 16, 'Clover'),
(57, 72, 81, 'Limed Spruce'), (57, 100, 19, 'Dell'), (58, 0, 32, 'Toledo'),
(58, 32, 16, 'Sambuca'), (58, 42, 106, 'Jacarta'), (58, 104, 108, 'William'),
(58, 106, 71, 'Killarney'), (58, 176, 158, 'Keppel'), (59, 0, 11,
'Temptress'), (59, 9, 16, 'Aubergine'), (59, 31, 31, 'Jon'), (59, 40, 32,
'Treehouse'), (59, 122, 87, 'Amazon'), (59, 145, 180, 'Boston Blue'), (60, 8,
120, 'Windsor'), (60, 18, 6, 'Rebel'), (60, 31, 118, 'Meteorite'), (60, 32, 5,
'Dark Ebony'), (60, 57, 16, 'Camouflage'), (60, 65, 81, 'Bright Gray'), (60,
68, 67, 'Cape Cod'), (60, 73, 58, 'Lunar Green'), (61, 12, 2, 'Bean  '), (61,
43, 31, 'Bistre'), (61, 125, 82, 'Goblin'), (62, 4, 128, 'Kingfisher Daisy'),
(62, 28, 20, 'Cedar'), (62, 43, 35, 'English Walnut'), (62, 44, 28, 'Black Marlin'), 
(62, 58, 68, 'Ship Gray'), (62, 171, 191, 'Pelorous'), (63, 33, 9,
'Bronze'), (63, 37, 0, 'Cola'), (63, 48, 2, 'Madras'), (63, 48, 127, 'Minsk'),
(63, 76, 58, 'Cabbage Pont'), (63, 88, 59, 'Tom Thumb'), (63, 93, 83, 'Mineral Green'), 
(63, 193, 170, 'Puerto Rico'), (63, 255, 0, 'Harlequin'), (64, 24, 1,
'Brown Pod'), (64, 41, 29, 'Cork'), (64, 59, 56, 'Masala'), (64, 61, 25,
'Thatch Green'), (64, 81, 105, 'Fiord'), (64, 130, 109, 'Viridian'), (64, 168,
96, 'Chateau Green'), (65, 0, 86, 'Ripe Plum'), (65, 31, 16, 'Paco'), (65, 32,
16, 'Deep Oak'), (65, 60, 55, 'Merlin'), (65, 66, 87, 'Gun Powder'), (65, 76,
125, 'East Bay'), (65, 105, 225, 'Royal Blue'), (65, 170, 120, 'Ocean Green'),
(66, 3, 3, 'Burnt Maroon'), (66, 57, 33, 'Lisbon Brown'), (66, 121, 119,
'Faded Jade'), (67, 21, 96, 'Scarlet Gum'), (67, 49, 32, 'Iroko'), (67, 62,
55, 'Armadillo'), (67, 76, 89, 'River Bed'), (67, 106, 13, 'Green Leaf'), (68,
1, 45, 'Barossa'), (68, 29, 0, 'Morocco Brown'), (68, 73, 84, 'Mako'), (69,
73, 54, 'Kelp'), (69, 108, 172, 'San Marino'), (69, 177, 232, 'Picton Blue'),
(70, 11, 65, 'Loulou'), (70, 36, 37, 'Crater Brown'), (70, 89, 69, 'Gray Asparagus'), 
(70, 130, 180, 'Steel Blue'), (72, 4, 4, 'Rustic Red'), (72, 6,
7, 'Bulgarian Rose'), (72, 6, 86, 'Clairvoyant'), (72, 28, 28, 'Cocoa Bean'),
(72, 49, 49, 'Woody Brown'), (72, 60, 50, 'Taupe'), (73, 23, 12, 'Van Cleef'),
(73, 38, 21, 'Brown Derby'), (73, 55, 27, 'Metallic Bronze'), (73, 84, 0,
'Verdun Green'), (73, 102, 121, 'Blue Bayoux'), (73, 113, 131, 'Bismark'),
(74, 42, 4, 'Bracken'), (74, 48, 4, 'Deep Bronze'), (74, 60, 48, 'Mondo'),
(74, 66, 68, 'Tundora'), (74, 68, 75, 'Gravel'), (74, 78, 90, 'Trout'), (75,
0, 130, 'Pigment Indigo'), (75, 93, 82, 'Nandor'), (76, 48, 36, 'Saddle'),
(76, 79, 86, 'Abbey'), (77, 1, 53, 'Blackberry'), (77, 10, 24, 'Cab Sav'),
(77, 30, 1, 'Indian Tan'), (77, 40, 45, 'Cowboy'), (77, 40, 46, 'Livid Brown'), 
(77, 56, 51, 'Rock'), (77, 61, 20, 'Punga'), (77, 64, 15,
'Bronzetone'), (77, 83, 40, 'Woodland'), (78, 6, 6, 'Mahogany'), (78, 42, 90,
'Bossanova'), (78, 59, 65, 'Matterhorn'), (78, 66, 12, 'Bronze Olive'), (78,
69, 98, 'Mulled Wine'), (78, 102, 73, 'Axolotl'), (78, 127, 158, 'Wedgewood'),
(78, 171, 209, 'Shakespeare'), (79, 28, 112, 'Honey Flower'), (79, 35, 152,
'Daisy Bush'), (79, 105, 198, 'Indigo'), (79, 121, 66, 'Fern Green'), (79,
157, 93, 'Fruit Salad'), (79, 168, 61, 'Apple'), (80, 67, 81, 'Mortar'), (80,
112, 150, 'Kashmir Blue'), (80, 118, 114, 'Cutty Sark'), (80, 200, 120,
'Emerald'), (81, 70, 73, 'Emperor'), (81, 110, 61, 'Chalet Green'), (81, 124,
102, 'Como'), (81, 128, 143, 'Smalt Blue'), (82, 0, 31, 'Castro'), (82, 12,
23, 'Maroon Oak'), (82, 60, 148, 'Gigas'), (83, 52, 85, 'Voodoo'), (83, 68,
145, 'Victoria'), (83, 130, 75, 'Hippie Green'), (84, 16, 18, 'Heath'), (84,
67, 51, 'Judge Gray'), (84, 83, 77, 'Fuscous Gray'), (84, 144, 25, 'Vida Loca'), 
(85, 40, 12, 'Cioccolato'), (85, 91, 16, 'Saratoga'), (85, 109, 86,
'Finlandia'), (85, 144, 217, 'Havelock Blue'), (86, 180, 190, 'Fountain Blue'), 
(87, 131, 99, 'Spring Leaves'), (88, 52, 1, 'Saddle Brown'), (88, 85,
98, 'Scarpa Flow'), (88, 113, 86, 'Cactus'), (88, 154, 175, 'Hippie Blue'),
(89, 29, 53, 'Wine Berry'), (89, 40, 4, 'Brown Bramble'), (89, 55, 55, 'Congo Brown'), 
(89, 68, 51, 'Millbrook'), (90, 110, 156, 'Waikawa Gray'), (90, 135,
160, 'Horizon'), (91, 48, 19, 'Jambalaya'), (92, 1, 32, 'Bordeaux'), (92, 5,
54, 'Mulberry Wood'), (92, 46, 1, 'Carnaby Tan'), (92, 93, 117, 'Comet'), (93,
30, 15, 'Redwood'), (93, 76, 81, 'Don Juan'), (93, 92, 88, 'Chicago'), (93,
94, 55, 'Verdigris'), (93, 119, 71, 'Dingley'), (93, 161, 159, 'Breaker Bay'),
(94, 72, 62, 'Kabul'), (94, 93, 59, 'Hemlock'), (95, 61, 38, 'Irish Coffee'),
(95, 95, 110, 'Mid Gray'), (95, 102, 114, 'Shuttle Gray'), (95, 167, 119,
'Aqua Forest'), (95, 179, 172, 'Tradewind'), (96, 73, 19, 'Horses Neck'), (96,
91, 115, 'Smoky'), (96, 110, 104, 'Corduroy'), (96, 147, 209, 'Danube'), (97,
39, 24, 'Espresso'), (97, 64, 81, 'Eggplant'), (97, 93, 48, 'Costa Del Sol'),
(97, 132, 95, 'Glade Green'), (98, 47, 48, 'Buccaneer'), (98, 63, 45,
'Quincy'), (98, 78, 154, 'Butterfly Bush'), (98, 81, 25, 'West Coast'), (98,
102, 73, 'Finch'), (99, 154, 143, 'Patina'), (99, 183, 108, 'Fern'), (100, 86,
183, 'Blue Violet'), (100, 96, 119, 'Dolphin'), (100, 100, 99, 'Storm Dust'),
(100, 106, 84, 'Siam'), (100, 110, 117, 'Nevada'), (100, 149, 237, 'Cornflower Blue'), 
(100, 204, 219, 'Viking'), (101, 0, 11, 'Rosewood'), (101, 26, 20,
'Cherrywood'), (101, 45, 193, 'Purple Heart'), (101, 114, 32, 'Fern Frond'),
(101, 116, 93, 'Willow Grove'), (101, 134, 159, 'Hoki'), (102, 0, 69,
'Pompadour'), (102, 0, 153, 'Purple'), (102, 2, 60, 'Tyrian Purple'), (102,
16, 16, 'Dark Tan'), (102, 181, 143, 'Silver Tree'), (102, 255, 0, 'Bright Green'), 
(102, 255, 102, "Screamin' Green"), (103, 3, 45, 'Black Rose'), (103,
95, 166, 'Scampi'), (103, 102, 98, 'Ironside Gray'), (103, 137, 117, 'Viridian Green'), 
(103, 167, 18, 'Christi'), (104, 54, 0, 'Nutmeg Wood Finish'), (104,
85, 88, 'Zambezi'), (104, 94, 110, 'Salt Box'), (105, 37, 69, 'Tawny Port'),
(105, 45, 84, 'Finn'), (105, 95, 98, 'Scorpion'), (105, 126, 154, 'Lynch'),
(106, 68, 46, 'Spice'), (106, 93, 27, 'Himalaya'), (106, 96, 81, 'Soya Bean'),
(107, 42, 20, 'Hairy Heath'), (107, 63, 160, 'Royal Purple'), (107, 78, 49,
'Shingle Fawn'), (107, 87, 85, 'Dorado'), (107, 139, 162, 'Bermuda Gray'),
(107, 142, 35, 'Olive Drab'), (108, 48, 130, 'Eminence'), (108, 218, 231,
'Turquoise Blue'), (109, 1, 1, 'Lonestar'), (109, 94, 84, 'Pine Cone'), (109,
108, 108, 'Dove Gray'), (109, 146, 146, 'Juniper'), (109, 146, 161, 'Gothic'),
(110, 9, 2, 'Red Oxide'), (110, 29, 20, 'Moccaccino'), (110, 72, 38, 'Pickled Bean'), 
(110, 75, 38, 'Dallas'), (110, 109, 87, 'Kokoda'), (110, 119, 131,
'Pale Sky'), (111, 68, 12, 'Cafe Royale'), (111, 106, 97, 'Flint'), (111, 142,
99, 'Highland'), (111, 157, 2, 'Limeade'), (111, 208, 197, 'Downy'), (112, 28,
28, 'Persian Plum'), (112, 66, 20, 'Sepia'), (112, 74, 7, 'Antique Bronze'),
(112, 79, 80, 'Ferra'), (112, 101, 85, 'Coffee'), (112, 128, 144, 'Slate Gray'), 
(113, 26, 0, 'Cedar Wood Finish'), (113, 41, 29, 'Metallic Copper'),
(113, 70, 147, 'Affair'), (113, 74, 178, 'Studio'), (113, 93, 71, 'Tobacco Brown'), 
(113, 99, 56, 'Yellow Metal'), (113, 107, 86, 'Peat'), (113, 110, 16,
'Olivetone'), (113, 116, 134, 'Storm Gray'), (113, 128, 128, 'Sirocco'), (113,
217, 226, 'Aquamarine Blue'), (114, 1, 15, 'Venetian Red'), (114, 74, 47, 'Old Copper'), 
(114, 109, 78, 'Go Ben'), (114, 123, 137, 'Raven'), (115, 30, 143,
'Seance'), (115, 74, 18, 'Raw Umber'), (115, 108, 159, 'Kimberly'), (115, 109,
88, 'Crocodile'), (115, 120, 41, 'Crete'), (115, 134, 120, 'Xanadu'), (116,
100, 13, 'Spicy Mustard'), (116, 125, 99, 'Limed Ash'), (116, 125, 131,
'Rolling Stone'), (116, 136, 129, 'Blue Smoke'), (116, 147, 120, 'Laurel'),
(116, 195, 101, 'Mantis'), (117, 90, 87, 'Russett'), (117, 99, 168, 'Deluge'),
(118, 57, 93, 'Cosmic'), (118, 102, 198, 'Blue Marguerite'), (118, 189, 23,
'Lima'), (118, 215, 234, 'Sky Blue'), (119, 15, 5, 'Dark Burgundy'), (119, 31,
31, 'Crown of Thorns'), (119, 63, 26, 'Walnut'), (119, 111, 97, 'Pablo'),
(119, 129, 32, 'Pacifika'), (119, 158, 134, 'Oxley'), (119, 221, 119, 'Pastel Green'), 
(120, 1, 9, 'Japanese Maple'), (120, 45, 25, 'Mocha'), (120, 47, 22,
'Peanut'), (120, 134, 107, 'Camouflage Green'), (120, 138, 37, 'Wasabi'),
(120, 139, 186, 'Ship Cove'), (120, 163, 156, 'Sea Nymph'), (121, 93, 76,
'Roman Coffee'), (121, 104, 120, 'Old Lavender'), (121, 105, 137, 'Rum'),
(121, 106, 120, 'Fedora'), (121, 109, 98, 'Sandstone'), (121, 222, 236,
'Spray'), (122, 1, 58, 'Siren'), (122, 88, 193, 'Fuchsia Blue'), (122, 122,
122, 'Boulder'), (122, 137, 184, 'Wild Blue Yonder'), (122, 196, 136, 'De York'), 
(123, 56, 1, 'Red Beech'), (123, 63, 0, 'Cinnamon'), (123, 102, 8,
'Yukon Gold'), (123, 120, 116, 'Tapa'), (123, 124, 148, 'Waterloo '), (123,
130, 101, 'Flax Smoke'), (123, 159, 128, 'Amulet'), (123, 160, 91,
'Asparagus'), (124, 28, 5, 'Kenyan Copper'), (124, 118, 49, 'Pesto'), (124,
119, 138, 'Topaz'), (124, 123, 122, 'Concord'), (124, 123, 130, 'Jumbo'),
(124, 136, 26, 'Trendy Green'), (124, 161, 166, 'Gumbo'), (124, 176, 161,
'Acapulco'), (124, 183, 187, 'Neptune'), (125, 44, 20, 'Pueblo'), (125, 169,
141, 'Bay Leaf'), (125, 200, 247, 'Malibu'), (125, 216, 198, 'Bermuda'), (126,
58, 21, 'Copper Canyon'), (127, 23, 52, 'Claret'), (127, 58, 2, 'Peru Tan'),
(127, 98, 109, 'Falcon'), (127, 117, 137, 'Mobster'), (127, 118, 211, 'Moody Blue'), 
(127, 255, 0, 'Chartreuse'), (127, 255, 212, 'Aquamarine'), (128, 0,
0, 'Maroon'), (128, 11, 71, 'Rose Bud Cherry'), (128, 24, 24, 'Falu Red'),
(128, 52, 31, 'Red Robin'), (128, 55, 144, 'Vivid Violet'), (128, 70, 27,
'Russet'), (128, 126, 121, 'Friar Gray'), (128, 128, 0, 'Olive'), (128, 128,
128, 'Gray'), (128, 179, 174, 'Gulf Stream'), (128, 179, 196, 'Glacier'),
(128, 204, 234, 'Seagull'), (129, 66, 44, 'Nutmeg'), (129, 110, 113, 'Spicy Pink'), 
(129, 115, 119, 'Empress'), (129, 152, 133, 'Spanish Green'), (130,
111, 101, 'Sand Dune'), (130, 134, 133, 'Gunsmoke'), (130, 143, 114,
'Battleship Gray'), (131, 25, 35, 'Merlot'), (131, 112, 80, 'Shadow'), (131,
170, 93, 'Chelsea Cucumber'), (131, 208, 198, 'Monte Carlo'), (132, 49, 121,
'Plum'), (132, 160, 160, 'Granny Smith'), (133, 129, 217, 'Chetwode Blue'),
(133, 132, 112, 'Bandicoot'), (133, 159, 175, 'Bali Hai'), (133, 196, 204,
'Half Baked'), (134, 1, 17, 'Red Devil'), (134, 60, 60, 'Lotus'), (134, 72,
60, 'Ironstone'), (134, 77, 30, 'Bull Shot'), (134, 86, 10, 'Rusty Nail'),
(134, 137, 116, 'Bitter'), (134, 148, 159, 'Regent Gray'), (135, 21, 80,
'Disco'), (135, 117, 110, 'Americano'), (135, 124, 123, 'Hurricane'), (135,
141, 145, 'Oslo Gray'), (135, 171, 57, 'Sushi'), (136, 83, 66, 'Spicy Mix'),
(136, 98, 33, 'Kumera'), (136, 131, 135, 'Suva Gray'), (136, 141, 101,
'Avocado'), (137, 52, 86, 'Camelot'), (137, 56, 67, 'Solid Pink'), (137, 67,
103, 'Cannon Pink'), (137, 125, 109, 'Makara'), (138, 51, 36, 'Burnt Umber'),
(138, 115, 214, 'True V'), (138, 131, 96, 'Clay Creek'), (138, 131, 137,
'Monsoon'), (138, 143, 138, 'Stack'), (138, 185, 241, 'Jordy Blue'), (139, 0,
255, 'Electric Violet'), (139, 7, 35, 'Monarch'), (139, 107, 11, 'Corn Harvest'), 
(139, 132, 112, 'Olive Haze'), (139, 132, 126, 'Schooner'), (139,
134, 128, 'Natural Gray'), (139, 156, 144, 'Mantle'), (139, 159, 238,
'Portage'), (139, 166, 144, 'Envy'), (139, 169, 165, 'Cascade'), (139, 230,
216, 'Riptide'), (140, 5, 94, 'Cardinal Pink'), (140, 71, 47, 'Mule Fawn'),
(140, 87, 56, 'Potters Clay'), (140, 100, 149, 'Trendy Pink'), (141, 2, 38,
'Paprika'), (141, 61, 56, 'Sanguine Brown'), (141, 63, 63, 'Tosca'), (141,
118, 98, 'Cement'), (141, 137, 116, 'Granite Green'), (141, 144, 161,
'Manatee'), (141, 168, 204, 'Polo Blue'), (142, 0, 0, 'Red Berry'), (142, 77,
30, 'Rope'), (142, 111, 112, 'Opium'), (142, 119, 94, 'Domino'), (142, 129,
144, 'Mamba'), (142, 171, 193, 'Nepal'), (143, 2, 28, 'Pohutukawa'), (143, 62,
51, 'El Salva'), (143, 75, 14, 'Korma'), (143, 129, 118, 'Squirrel'), (143,
214, 180, 'Vista Blue'), (144, 0, 32, 'Burgundy'), (144, 30, 30, 'Old Brick'),
(144, 120, 116, 'Hemp'), (144, 123, 113, 'Almond Frost'), (144, 141, 57,
'Sycamore'), (146, 0, 10, 'Sangria'), (146, 67, 33, 'Cumin'), (146, 111, 91,
'Beaver'), (146, 133, 115, 'Stonewall'), (146, 133, 144, 'Venus'), (147, 112,
219, 'Medium Purple'), (147, 204, 234, 'Cornflower'), (147, 223, 184, 'Algae Green'), 
(148, 71, 71, 'Copper Rust'), (148, 135, 113, 'Arrowtown'), (149, 0,
21, 'Scarlett'), (149, 99, 135, 'Strikemaster'), (149, 147, 150, 'Mountain Mist'), 
(150, 0, 24, 'Carmine'), (150, 75, 0, 'Brown'), (150, 112, 89,
'Leather'), (150, 120, 182, "Purple Mountain's Majesty"), (150, 123, 182,
'Lavender Purple'), (150, 168, 161, 'Pewter'), (150, 187, 171, 'Summer Green'), 
(151, 96, 93, 'Au Chico'), (151, 113, 181, 'Wisteria'), (151, 205,
45, 'Atlantis'), (152, 61, 97, 'Vin Rouge'), (152, 116, 211, 'Lilac Bush'),
(152, 119, 123, 'Bazaar'), (152, 129, 27, 'Hacienda'), (152, 141, 119, 'Pale Oyster'), 
(152, 255, 152, 'Mint Green'), (153, 0, 102, 'Fresh Eggplant'),
(153, 17, 153, 'Violet Eggplant'), (153, 22, 19, 'Tamarillo'), (153, 27, 7,
'Totem Pole'), (153, 102, 102, 'Copper Rose'), (153, 102, 204, 'Amethyst'),
(153, 122, 141, 'Mountbatten Pink'), (153, 153, 204, 'Blue Bell'), (154, 56,
32, 'Prairie Sand'), (154, 110, 97, 'Toast'), (154, 149, 119, 'Gurkha'), (154,
185, 115, 'Olivine'), (154, 194, 184, 'Shadow Green'), (155, 71, 3, 'Oregon'),
(155, 158, 143, 'Lemon Grass'), (156, 51, 54, 'Stiletto'), (157, 86, 22,
'Hawaiian Tan'), (157, 172, 183, 'Gull Gray'), (157, 194, 9, 'Pistachio'),
(157, 224, 147, 'Granny Smith Apple'), (157, 229, 255, 'Anakiwa'), (158, 83,
2, 'Chelsea Gem'), (158, 91, 64, 'Sepia Skin'), (158, 165, 135, 'Sage'), (158,
169, 31, 'Citron'), (158, 177, 205, 'Rock Blue'), (158, 222, 224, 'Morning Glory'), 
(159, 56, 29, 'Cognac'), (159, 130, 28, 'Reef Gold'), (159, 159, 156,
'Star Dust'), (159, 160, 177, 'Santas Gray'), (159, 215, 211, 'Sinbad'), (159,
221, 140, 'Feijoa'), (160, 39, 18, 'Tabasco'), (161, 117, 13, 'Buttered Rum'),
(161, 173, 181, 'Hit Gray'), (161, 197, 10, 'Citrus'), (161, 218, 215, 'Aqua Island'), 
(161, 233, 222, 'Water Leaf'), (162, 0, 109, 'Flirt'), (162, 59,
108, 'Rouge'), (162, 102, 69, 'Cape Palliser'), (162, 170, 179, 'Gray Chateau'), 
(162, 174, 171, 'Edward'), (163, 128, 123, 'Pharlap'), (163, 151,
180, 'Amethyst Smoke'), (163, 227, 237, 'Blizzard Blue'), (164, 164, 157,
'Delta'), (164, 166, 211, 'Wistful'), (164, 175, 110, 'Green Smoke'), (165,
11, 94, 'Jazzberry Jam'), (165, 155, 145, 'Zorba'), (165, 203, 12, 'Bahia'),
(166, 47, 32, 'Roof Terracotta'), (166, 85, 41, 'Paarl'), (166, 139, 91,
'Barley Corn'), (166, 146, 121, 'Donkey Brown'), (166, 162, 154, 'Dawn'),
(167, 37, 37, 'Mexican Red'), (167, 136, 44, 'Luxor Gold'), (168, 83, 7, 'Rich Gold'), 
(168, 101, 21, 'Reno Sand'), (168, 107, 107, 'Coral Tree'), (168, 152,
155, 'Dusty Gray'), (168, 153, 230, 'Dull Lavender'), (168, 165, 137,
'Tallow'), (168, 174, 156, 'Bud'), (168, 175, 142, 'Locust'), (168, 189, 159,
'Norway'), (168, 227, 189, 'Chinook'), (169, 164, 145, 'Gray Olive'), (169,
172, 182, 'Aluminium'), (169, 178, 195, 'Cadet Blue'), (169, 180, 151,
'Schist'), (169, 189, 191, 'Tower Gray'), (169, 190, 242, 'Perano'), (169,
198, 194, 'Opal'), (170, 55, 90, 'Night Shadz'), (170, 66, 3, 'Fire'), (170,
139, 91, 'Muesli'), (170, 141, 111, 'Sandal'), (170, 165, 169, 'Shady Lady'),
(170, 169, 205, 'Logan'), (170, 171, 183, 'Spun Pearl'), (170, 214, 230,
'Regent St Blue'), (170, 240, 209, 'Magic Mint'), (171, 5, 99, 'Lipstick'),
(171, 52, 114, 'Royal Heath'), (171, 145, 122, 'Sandrift'), (171, 160, 217,
'Cold Purple'), (171, 161, 150, 'Bronco'), (172, 138, 86, 'Limed Oak'), (172,
145, 206, 'East Side'), (172, 158, 34, 'Lemon Ginger'), (172, 164, 148,
'Napa'), (172, 165, 134, 'Hillary'), (172, 165, 159, 'Cloudy'), (172, 172,
172, 'Silver Chalice'), (172, 183, 142, 'Swamp Green'), (172, 203, 177,
'Spring Rain'), (172, 221, 77, 'Conifer'), (172, 225, 175, 'Celadon'), (173,
120, 27, 'Mandalay'), (173, 190, 209, 'Casper'), (173, 223, 173, 'Moss Green'), 
(173, 230, 196, 'Padua'), (173, 255, 47, 'Green Yellow'), (174, 69,
96, 'Hippie Pink'), (174, 96, 32, 'Desert'), (174, 128, 158, 'Bouquet'), (175,
64, 53, 'Medium Carmine'), (175, 77, 67, 'Apple Blossom'), (175, 89, 62,
'Brown Rust'), (175, 135, 81, 'Driftwood'), (175, 143, 44, 'Alpine'), (175,
159, 28, 'Lucky'), (175, 160, 158, 'Martini'), (175, 177, 184, 'Bombay'),
(175, 189, 217, 'Pigeon Post'), (176, 76, 106, 'Cadillac'), (176, 93, 84,
'Matrix'), (176, 94, 129, 'Tapestry'), (176, 102, 8, 'Mai Tai'), (176, 154,
149, 'Del Rio'), (176, 224, 230, 'Powder Blue'), (176, 227, 19, 'Inch Worm'),
(177, 0, 0, 'Bright Red'), (177, 74, 11, 'Vesuvius'), (177, 97, 11, 'Pumpkin Skin'), 
(177, 109, 82, 'Santa Fe'), (177, 148, 97, 'Teak'), (177, 226, 193,
'Fringy Flower'), (177, 244, 231, 'Ice Cold'), (178, 9, 49, 'Shiraz'), (178,
161, 234, 'Biloba Flower'), (179, 45, 41, 'Tall Poppy'), (179, 82, 19, 'Fiery Orange'), 
(179, 128, 7, 'Hot Toddy'), (179, 175, 149, 'Taupe Gray'), (179,
193, 16, 'La Rioja'), (180, 51, 50, 'Well Read'), (180, 70, 104, 'Blush'),
(180, 207, 211, 'Jungle Mist'), (181, 114, 129, 'Turkish Rose'), (181, 126,
220, 'Lavender'), (181, 162, 127, 'Mongoose'), (181, 179, 92, 'Olive Green'),
(181, 210, 206, 'Jet Stream'), (181, 236, 223, 'Cruise'), (182, 49, 108,
'Hibiscus'), (182, 157, 152, 'Thatch'), (182, 176, 149, 'Heathered Gray'),
(182, 186, 164, 'Eagle'), (182, 209, 234, 'Spindle'), (182, 211, 191, 'Gum Leaf'), 
(183, 65, 14, 'Rust'), (183, 142, 92, 'Muddy Waters'), (183, 162, 20,
'Sahara'), (183, 164, 88, 'Husk'), (183, 177, 177, 'Nobel'), (183, 195, 208,
'Heather'), (183, 240, 190, 'Madang'), (184, 17, 4, 'Milano Red'), (184, 115,
51, 'Copper'), (184, 181, 106, 'Gimblet'), (184, 193, 177, 'Green Spring'),
(184, 194, 93, 'Celery'), (184, 224, 249, 'Sail'), (185, 78, 72, 'Chestnut'),
(185, 81, 64, 'Crail'), (185, 141, 40, 'Marigold'), (185, 196, 106, 'Wild Willow'), 
(185, 200, 172, 'Rainee'), (186, 1, 1, 'Guardsman Red'), (186, 69,
12, 'Rock Spray'), (186, 111, 30, 'Bourbon'), (186, 127, 3, 'Pirate Gold'),
(186, 177, 162, 'Nomad'), (186, 199, 201, 'Submarine'), (186, 238, 249,
'Charlotte'), (187, 51, 133, 'Medium Red Violet'), (187, 137, 131, 'Brandy Rose'), 
(187, 208, 9, 'Rio Grande'), (187, 215, 193, 'Surf'), (188, 201, 194,
'Powder Ash'), (189, 94, 46, 'Tuscany'), (189, 151, 142, 'Quicksand'), (189,
177, 168, 'Silk'), (189, 178, 161, 'Malta'), (189, 179, 199, 'Chatelle'),
(189, 187, 215, 'Lavender Gray'), (189, 189, 198, 'French Gray'), (189, 200,
179, 'Clay Ash'), (189, 201, 206, 'Loblolly'), (189, 237, 253, 'French Pass'),
(190, 166, 195, 'London Hue'), (190, 181, 183, 'Pink Swan'), (190, 222, 13,
'Fuego'), (191, 85, 0, 'Rose of Sharon'), (191, 184, 176, 'Tide'), (191, 190,
216, 'Blue Haze'), (191, 193, 194, 'Silver Sand'), (191, 201, 33, 'Key Lime Pie'), 
(191, 219, 226, 'Ziggurat'), (191, 255, 0, 'Lime'), (192, 43, 24,
'Thunderbird'), (192, 71, 55, 'Mojo'), (192, 128, 129, 'Old Rose'), (192, 192,
192, 'Silver'), (192, 211, 185, 'Pale Leaf'), (192, 216, 182, 'Pixie Green'),
(193, 68, 14, 'Tia Maria'), (193, 84, 193, 'Fuchsia Pink'), (193, 160, 4,
'Buddha Gold'), (193, 183, 164, 'Bison Hide'), (193, 186, 176, 'Tea'), (193,
190, 205, 'Gray Suit'), (193, 215, 176, 'Sprout'), (193, 240, 124, 'Sulu'),
(194, 107, 3, 'Indochine'), (194, 149, 93, 'Twine'), (194, 189, 182, 'Cotton Seed'), 
(194, 202, 196, 'Pumice'), (194, 232, 229, 'Jagged Ice'), (195, 33,
72, 'Maroon Flush'), (195, 176, 145, 'Indian Khaki'), (195, 191, 193, 'Pale Slate'), 
(195, 195, 189, 'Gray Nickel'), (195, 205, 230, 'Periwinkle Gray'),
(195, 209, 209, 'Tiara'), (195, 221, 249, 'Tropical Blue'), (196, 30, 58,
'Cardinal'), (196, 86, 85, 'Fuzzy Wuzzy Brown'), (196, 87, 25, 'Orange Roughy'), 
(196, 196, 188, 'Mist Gray'), (196, 208, 176, 'Coriander'), (196,
244, 235, 'Mint Tulip'), (197, 75, 140, 'Mulberry'), (197, 153, 34, 'Nugget'),
(197, 153, 75, 'Tussock'), (197, 219, 202, 'Sea Mist'), (197, 225, 122,
'Yellow Green'), (198, 45, 66, 'Brick Red'), (198, 114, 107, 'Contessa'),
(198, 145, 145, 'Oriental Pink'), (198, 168, 75, 'Roti'), (198, 195, 181,
'Ash'), (198, 200, 189, 'Kangaroo'), (198, 230, 16, 'Las Palmas'), (199, 3,
30, 'Monza'), (199, 21, 133, 'Red Violet'), (199, 188, 162, 'Coral Reef'),
(199, 193, 255, 'Melrose'), (199, 196, 191, 'Cloud'), (199, 201, 213,
'Ghost'), (199, 205, 144, 'Pine Glade'), (199, 221, 229, 'Botticelli'), (200,
138, 101, 'Antique Brass'), (200, 162, 200, 'Lilac'), (200, 165, 40, 'Hokey Pokey'), 
(200, 170, 191, 'Lily'), (200, 181, 104, 'Laser'), (200, 227, 215,
'Edgewater'), (201, 99, 35, 'Piper'), (201, 148, 21, 'Pizza'), (201, 160, 220,
'Light Wisteria'), (201, 178, 155, 'Rodeo Dust'), (201, 179, 91, 'Sundance'),
(201, 185, 59, 'Earls Green'), (201, 192, 187, 'Silver Rust'), (201, 217, 210,
'Conch'), (201, 255, 162, 'Reef'), (201, 255, 229, 'Aero Blue'), (202, 52, 53,
'Flush Mahogany'), (202, 187, 72, 'Turmeric'), (202, 220, 212, 'Paris White'),
(202, 224, 13, 'Bitter Lemon'), (202, 230, 218, 'Skeptic'), (203, 143, 169,
'Viola'), (203, 202, 182, 'Foggy Gray'), (203, 211, 176, 'Green Mist'), (203,
219, 214, 'Nebula'), (204, 51, 51, 'Persian Red'), (204, 85, 0, 'Burnt Orange'), 
(204, 119, 34, 'Ochre'), (204, 136, 153, 'Puce'), (204, 202, 168,
'Thistle Green'), (204, 204, 255, 'Periwinkle'), (204, 255, 0, 'Electric Lime'), 
(205, 87, 0, 'Tenn'), (205, 92, 92, 'Chestnut Rose'), (205, 132, 41,
'Brandy Punch'), (205, 244, 255, 'Onahau'), (206, 185, 143, 'Sorrell Brown'),
(206, 186, 186, 'Cold Turkey'), (206, 194, 145, 'Yuma'), (206, 199, 167,
'Chino'), (207, 163, 157, 'Eunry'), (207, 181, 59, 'Old Gold'), (207, 220,
207, 'Tasman'), (207, 229, 210, 'Surf Crest'), (207, 249, 243, 'Hummingbird'), 
(207, 250, 244, 'Scandal'), (208, 95, 4, 'Red Stage'), (208, 109, 161,
'Hopbush'), (208, 125, 18, 'Meteor'), (208, 190, 248, 'Perfume'), (208, 192,
229, 'Prelude'), (208, 240, 192, 'Tea Green'), (209, 143, 27, 'Geebung'),
(209, 190, 168, 'Vanilla'), (209, 198, 180, 'Soft Amber'), (209, 210, 202,
'Celeste'), (209, 210, 221, 'Mischka'), (209, 226, 49, 'Pear'), (210, 105, 30,
'Hot Cinnamon'), (210, 125, 70, 'Raw Sienna'), (210, 158, 170, 'Careys Pink'),
(210, 180, 140, 'Tan'), (210, 218, 151, 'Deco'), (210, 246, 222, 'Blue Romance'), 
(210, 248, 176, 'Gossip'), (211, 203, 186, 'Sisal'), (211, 205,
197, 'Swirl'), (212, 116, 148, 'Charm'), (212, 182, 175, 'Clam Shell'), (212,
191, 141, 'Straw'), (212, 196, 168, 'Akaroa'), (212, 205, 22, 'Bird Flower'),
(212, 215, 217, 'Iron'), (212, 223, 226, 'Geyser'), (212, 226, 252, 'Hawkes Blue'), 
(213, 70, 0, 'Grenadier'), (213, 145, 164, 'Can Can'), (213, 154, 111,
'Whiskey'), (213, 209, 149, 'Winter Hazel'), (213, 246, 227, 'Granny Apple'),
(214, 145, 136, 'My Pink'), (214, 197, 98, 'Tacha'), (214, 206, 246, 'Moonraker'), 
(214, 214, 209, 'Quill Gray'), (214, 255, 219, 'Snowy Mint'), (215,
131, 127, 'New York Pink'), (215, 196, 152, 'Pavlova'), (215, 208, 255,
'Fog'), (216, 68, 55, 'Valencia'), (216, 124, 99, 'Japonica'), (216, 191, 216,
'Thistle'), (216, 194, 213, 'Maverick'), (216, 252, 250, 'Foam'), (217, 73,
114, 'Cabaret'), (217, 147, 118, 'Burning Sand'), (217, 185, 155, 'Cameo'),
(217, 214, 207, 'Timberwolf'), (217, 220, 193, 'Tana'), (217, 228, 245, 'Link Water'), 
(217, 247, 255, 'Mabel'), (218, 50, 135, 'Cerise'), (218, 91, 56,
'Flame Pea'), (218, 99, 4, 'Bamboo'), (218, 106, 65, 'Red Damask'), (218, 112,
214, 'Orchid'), (218, 138, 103, 'Copperfield'), (218, 165, 32, 'Golden Grass'), 
(218, 236, 214, 'Zanah'), (218, 244, 240, 'Iceberg'), (218, 250, 255,
'Oyster Bay'), (219, 80, 121, 'Cranberry'), (219, 150, 144, 'Petite Orchid'),
(219, 153, 94, 'Di Serria'), (219, 219, 219, 'Alto'), (219, 255, 248, 'Frosted Mint'), 
(220, 20, 60, 'Crimson'), (220, 67, 51, 'Punch'), (220, 178, 12,
'Galliano'), (220, 180, 188, 'Blossom'), (220, 215, 71, 'Wattle'), (220, 217,
210, 'Westar'), (220, 221, 204, 'Moon Mist'), (220, 237, 180, 'Caper'), (220,
240, 234, 'Swans Down'), (221, 214, 213, 'Swiss Coffee'), (221, 249, 241,
'White Ice'), (222, 49, 99, 'Cerise Red'), (222, 99, 96, 'Roman'), (222, 166,
129, 'Tumbleweed'), (222, 186, 19, 'Gold Tips'), (222, 193, 150, 'Brandy'),
(222, 203, 198, 'Wafer'), (222, 212, 164, 'Sapling'), (222, 215, 23,
'Barberry'), (222, 229, 192, 'Beryl Green'), (222, 245, 255, 'Pattens Blue'),
(223, 115, 255, 'Heliotrope'), (223, 190, 111, 'Apache'), (223, 205, 111,
'Chenin'), (223, 207, 219, 'Lola'), (223, 236, 218, 'Willow Brook'), (223,
255, 0, 'Chartreuse Yellow'), (224, 176, 255, 'Mauve'), (224, 182, 70,
'Anzac'), (224, 185, 116, 'Harvest Gold'), (224, 192, 149, 'Calico'), (224,
255, 255, 'Baby Blue'), (225, 104, 101, 'Sunglo'), (225, 188, 100, 'Equator'),
(225, 192, 200, 'Pink Flare'), (225, 230, 214, 'Periglacial Blue'), (225, 234,
212, 'Kidnapper'), (225, 246, 232, 'Tara'), (226, 84, 101, 'Mandy'), (226,
114, 91, 'Terracotta'), (226, 137, 19, 'Golden Bell'), (226, 146, 192,
'Shocking'), (226, 148, 24, 'Dixie'), (226, 156, 210, 'Light Orchid'), (226,
216, 237, 'Snuff'), (226, 235, 237, 'Mystic'), (226, 243, 236, 'Apple Green'),
(227, 11, 92, 'Razzmatazz'), (227, 38, 54, 'Alizarin Crimson'), (227, 66, 52,
'Cinnabar'), (227, 190, 190, 'Cavern Pink'), (227, 245, 225, 'Peppermint'),
(227, 249, 136, 'Mindaro'), (228, 118, 152, 'Deep Blush'), (228, 155, 15,
'Gamboge'), (228, 194, 213, 'Melanie'), (228, 207, 222, 'Twilight'), (228,
209, 192, 'Bone'), (228, 212, 34, 'Sunflower'), (228, 213, 183, 'Grain Brown'), 
(228, 214, 155, 'Zombie'), (228, 246, 231, 'Frostee'), (228, 255,
209, 'Snow Flurry'), (229, 43, 80, 'Amaranth'), (229, 132, 27, 'Zest'), (229,
204, 201, 'Dust Storm'), (229, 215, 189, 'Stark White'), (229, 216, 175,
'Hampton'), (229, 224, 225, 'Bon Jour'), (229, 229, 229, 'Mercury'), (229,
249, 246, 'Polar'), (230, 78, 3, 'Trinidad'), (230, 190, 138, 'Gold Sand'),
(230, 190, 165, 'Cashmere'), (230, 215, 185, 'Double Spanish White'), (230,
228, 212, 'Satin Linen'), (230, 242, 234, 'Harp'), (230, 248, 243, 'Off Green'), 
(230, 255, 233, 'Hint of Green'), (230, 255, 255, 'Tranquil'), (231,
114, 0, 'Mango Tango'), (231, 115, 10, 'Christine'), (231, 159, 140, 'Tonys Pink'), 
(231, 159, 196, 'Kobi'), (231, 188, 180, 'Rose Fog'), (231, 191, 5,
'Corn'), (231, 205, 140, 'Putty'), (231, 236, 230, 'Gray Nurse'), (231, 248,
255, 'Lily White'), (231, 254, 255, 'Bubbles'), (232, 153, 40, 'Fire Bush'),
(232, 185, 179, 'Shilo'), (232, 224, 213, 'Pearl Bush'), (232, 235, 224,
'Green White'), (232, 241, 212, 'Chrome White'), (232, 242, 235, 'Gin'), (232,
245, 242, 'Aqua Squeeze'), (233, 110, 0, 'Clementine'), (233, 116, 81, 'Burnt Sienna'), 
(233, 124, 7, 'Tahiti Gold'), (233, 206, 205, 'Oyster Pink'), (233,
215, 90, 'Confetti'), (233, 227, 227, 'Ebb'), (233, 248, 237, 'Ottoman'),
(233, 255, 253, 'Clear Day'), (234, 136, 168, 'Carissma'), (234, 174, 105,
'Porsche'), (234, 179, 59, 'Tulip Tree'), (234, 198, 116, 'Rob Roy'), (234,
218, 184, 'Raffia'), (234, 232, 212, 'White Rock'), (234, 246, 238,
'Panache'), (234, 246, 255, 'Solitude'), (234, 249, 245, 'Aqua Spring'), (234,
255, 254, 'Dew'), (235, 147, 115, 'Apricot'), (235, 194, 175, 'Zinnwaldite'),
(236, 169, 39, 'Fuel Yellow'), (236, 197, 78, 'Ronchi'), (236, 199, 238,
'French Lilac'), (236, 205, 185, 'Just Right'), (236, 224, 144, 'Wild Rice'),
(236, 235, 189, 'Fall Green'), (236, 235, 206, 'Aths Special'), (236, 242, 69,
'Starship'), (237, 10, 63, 'Red Ribbon'), (237, 122, 28, 'Tango'), (237, 145,
33, 'Carrot Orange'), (237, 152, 158, 'Sea Pink'), (237, 179, 129, 'Tacao'),
(237, 201, 175, 'Desert Sand'), (237, 205, 171, 'Pancho'), (237, 220, 177,
'Chamois'), (237, 234, 153, 'Primrose'), (237, 245, 221, 'Frost'), (237, 245,
245, 'Aqua Haze'), (237, 246, 255, 'Zumthor'), (237, 249, 241, 'Narvik'),
(237, 252, 132, 'Honeysuckle'), (238, 130, 238, 'Lavender Magenta'), (238,
193, 190, 'Beauty Bush'), (238, 215, 148, 'Chalky'), (238, 217, 196,
'Almond'), (238, 220, 130, 'Flax'), (238, 222, 218, 'Bizarre'), (238, 227,
173, 'Double Colonial White'), (238, 238, 232, 'Cararra'), (238, 239, 120,
'Manz'), (238, 240, 200, 'Tahuna Sands'), (238, 240, 243, 'Athens Gray'),
(238, 243, 195, 'Tusk'), (238, 244, 222, 'Loafer'), (238, 246, 247, 'Catskill White'), 
(238, 253, 255, 'Twilight Blue'), (238, 255, 154, 'Jonquil'), (238,
255, 226, 'Rice Flower'), (239, 134, 63, 'Jaffa'), (239, 239, 239, 'Gallery'),
(239, 242, 243, 'Porcelain'), (240, 145, 169, 'Mauvelous'), (240, 213, 45,
'Golden Dream'), (240, 219, 125, 'Golden Sand'), (240, 220, 130, 'Buff'),
(240, 226, 236, 'Prim'), (240, 230, 140, 'Khaki'), (240, 238, 253, 'Selago'),
(240, 238, 255, 'Titan White'), (240, 248, 255, 'Alice Blue'), (240, 252, 234,
'Feta'), (241, 130, 0, 'Gold Drop'), (241, 155, 171, 'Wewak'), (241, 231, 136,
'Sahara Sand'), (241, 233, 210, 'Parchment'), (241, 233, 255, 'Blue Chalk'),
(241, 238, 193, 'Mint Julep'), (241, 241, 241, 'Seashell'), (241, 247, 242,
'Saltpan'), (241, 255, 173, 'Tidal'), (241, 255, 200, 'Chiffon'), (242, 85,
42, 'Flamingo'), (242, 133, 0, 'Tangerine'), (242, 195, 178, 'Mandys Pink'),
(242, 242, 242, 'Concrete'), (242, 250, 250, 'Black Squeeze'), (243, 71, 35,
'Pomegranate'), (243, 173, 22, 'Buttercup'), (243, 214, 157, 'New Orleans'),
(243, 217, 223, 'Vanilla Ice'), (243, 231, 187, 'Sidecar'), (243, 233, 229,
'Dawn Pink'), (243, 237, 207, 'Wheatfield'), (243, 251, 98, 'Canary'), (243,
251, 212, 'Orinoco'), (243, 255, 216, 'Carla'), (244, 0, 161, 'Hollywood Cerise'), 
(244, 164, 96, 'Sandy brown'), (244, 196, 48, 'Saffron'), (244, 216,
28, 'Ripe Lemon'), (244, 235, 211, 'Janna'), (244, 242, 238, 'Pampas'), (244,
244, 244, 'Wild Sand'), (244, 248, 255, 'Zircon'), (245, 117, 132, 'Froly'),
(245, 200, 92, 'Cream Can'), (245, 201, 153, 'Manhattan'), (245, 213, 160,
'Maize'), (245, 222, 179, 'Wheat'), (245, 231, 162, 'Sandwisp'), (245, 231,
226, 'Pot Pourri'), (245, 233, 211, 'Albescent White'), (245, 237, 239, 'Soft Peach'), 
(245, 243, 229, 'Ecru White'), (245, 245, 220, 'Beige'), (245, 251,
61, 'Golden Fizz'), (245, 255, 190, 'Australian Mint'), (246, 74, 138, 'French Rose'), 
(246, 83, 166, 'Brilliant Rose'), (246, 164, 201, 'Illusion'), (246,
240, 230, 'Merino'), (246, 247, 247, 'Black Haze'), (246, 255, 220, 'Spring Sun'), 
(247, 70, 138, 'Violet Red'), (247, 119, 3, 'Chilean Fire'), (247, 127,
190, 'Persian Pink'), (247, 182, 104, 'Rajah'), (247, 200, 218, 'Azalea'),
(247, 219, 230, 'We Peep'), (247, 242, 225, 'Quarter Spanish White'), (247,
245, 250, 'Whisper'), (247, 250, 247, 'Snow Drift'), (248, 184, 83,
'Casablanca'), (248, 195, 223, 'Chantilly'), (248, 217, 233, 'Cherub'), (248,
219, 157, 'Marzipan'), (248, 221, 92, 'Energy Yellow'), (248, 228, 191,
'Givry'), (248, 240, 232, 'White Linen'), (248, 244, 255, 'Magnolia'), (248,
246, 241, 'Spring Wood'), (248, 247, 220, 'Coconut Cream'), (248, 247, 252,
'White Lilac'), (248, 248, 247, 'Desert Storm'), (248, 249, 156, 'Texas'),
(248, 250, 205, 'Corn Field'), (248, 253, 211, 'Mimosa'), (249, 90, 97,
'Carnation'), (249, 191, 88, 'Saffron Mango'), (249, 224, 237, 'Carousel Pink'), 
(249, 228, 188, 'Dairy Cream'), (249, 230, 99, 'Portica'), (249, 234,
243, 'Amour'), (249, 248, 228, 'Rum Swizzle'), (249, 255, 139, 'Dolly'), (249,
255, 246, 'Sugar Cane'), (250, 120, 20, 'Ecstasy'), (250, 157, 90, 'Tan Hide'), 
(250, 211, 162, 'Corvette'), (250, 223, 173, 'Peach Yellow'), (250,
230, 0, 'Turbo'), (250, 234, 185, 'Astra'), (250, 236, 204, 'Champagne'),
(250, 240, 230, 'Linen'), (250, 243, 240, 'Fantasy'), (250, 247, 214, 'Citrine White'), 
(250, 250, 250, 'Alabaster'), (250, 253, 228, 'Hint of Yellow'),
(250, 255, 164, 'Milan'), (251, 96, 127, 'Brink Pink'), (251, 137, 137,
'Geraldine'), (251, 160, 227, 'Lavender Rose'), (251, 161, 41, 'Sea Buckthorn'), 
(251, 172, 19, 'Sun'), (251, 174, 210, 'Lavender Pink'), (251,
178, 163, 'Rose Bud'), (251, 190, 218, 'Cupid'), (251, 204, 231, 'Classic Rose'), 
(251, 206, 177, 'Apricot Peach'), (251, 231, 178, 'Banana Mania'),
(251, 232, 112, 'Marigold Yellow'), (251, 233, 108, 'Festival'), (251, 234,
140, 'Sweet Corn'), (251, 236, 93, 'Candy Corn'), (251, 249, 249, 'Hint of Red'), 
(251, 255, 186, 'Shalimar'), (252, 15, 192, 'Shocking Pink'), (252,
128, 165, 'Tickle Me Pink'), (252, 156, 29, 'Tree Poppy'), (252, 192, 30,
'Lightning Yellow'), (252, 214, 103, 'Goldenrod'), (252, 217, 23,
'Candlelight'), (252, 218, 152, 'Cherokee'), (252, 244, 208, 'Double Pearl Lusta'), 
(252, 244, 220, 'Pearl Lusta'), (252, 248, 247, 'Vista White'), (252,
251, 243, 'Bianca'), (252, 254, 218, 'Moon Glow'), (252, 255, 231, 'China Ivory'), 
(252, 255, 249, 'Ceramic'), (253, 14, 53, 'Torch Red'), (253, 91,
120, 'Wild Watermelon'), (253, 123, 51, 'Crusta'), (253, 124, 7, 'Sorbus'),
(253, 159, 162, 'Sweet Pink'), (253, 213, 177, 'Light Apricot'), (253, 215,
228, 'Pig Pink'), (253, 225, 220, 'Cinderella'), (253, 226, 149, 'Golden Glow'), 
(253, 233, 16, 'Lemon'), (253, 245, 230, 'Old Lace'), (253, 246, 211,
'Half Colonial White'), (253, 247, 173, 'Drover'), (253, 254, 184, 'Pale Prim'), 
(253, 255, 213, 'Cumulus'), (254, 40, 162, 'Persian Rose'), (254, 76,
64, 'Sunset Orange'), (254, 111, 94, 'Bittersweet'), (254, 157, 4,
'California'), (254, 169, 4, 'Yellow Sea'), (254, 186, 173, 'Melon'), (254,
211, 60, 'Bright Sun'), (254, 216, 93, 'Dandelion'), (254, 219, 141,
'Salomie'), (254, 229, 172, 'Cape Honey'), (254, 235, 243, 'Remy'), (254, 239,
206, 'Oasis'), (254, 240, 236, 'Bridesmaid'), (254, 242, 199, 'Beeswax'),
(254, 243, 216, 'Bleach White'), (254, 244, 204, 'Pipi'), (254, 244, 219,
'Half Spanish White'), (254, 244, 248, 'Wisp Pink'), (254, 245, 241,
'Provincial Pink'), (254, 247, 222, 'Half Dutch White'), (254, 248, 226,
'Solitaire'), (254, 248, 255, 'White Pointer'), (254, 249, 227, 'Off Yellow'),
(254, 252, 237, 'Orange White'), (255, 0, 0, 'Red'), (255, 0, 127, 'Rose'),
(255, 0, 204, 'Purple Pizzazz'), (255, 0, 255, 'Magenta / Fuchsia'), (255, 36,
0, 'Scarlet'), (255, 51, 153, 'Wild Strawberry'), (255, 51, 204, 'Razzle Dazzle Rose'), 
(255, 53, 94, 'Radical Red'), (255, 63, 52, 'Red Orange'),
(255, 64, 64, 'Coral Red'), (255, 77, 0, 'Vermilion'), (255, 79, 0,
'International Orange'), (255, 96, 55, 'Outrageous Orange'), (255, 102, 0,
'Blaze Orange'), (255, 102, 255, 'Pink Flamingo'), (255, 104, 31, 'Orange'),
(255, 105, 180, 'Hot Pink'), (255, 107, 83, 'Persimmon'), (255, 111, 255,
'Blush Pink'), (255, 112, 52, 'Burning Orange'), (255, 117, 24, 'Pumpkin'),
(255, 125, 7, 'Flamenco'), (255, 127, 0, 'Flush Orange'), (255, 127, 80,
'Coral'), (255, 140, 105, 'Salmon'), (255, 144, 0, 'Pizazz'), (255, 145, 15,
'West Side'), (255, 145, 164, 'Pink Salmon'), (255, 153, 51, 'Neon Carrot'),
(255, 153, 102, 'Atomic Tangerine'), (255, 153, 128, 'Vivid Tangerine'), (255,
158, 44, 'Sunshade'), (255, 160, 0, 'Orange Peel'), (255, 161, 148, 'Mona Lisa'), 
(255, 165, 0, 'Web Orange'), (255, 166, 201, 'Carnation Pink'), (255,
171, 129, 'Hit Pink'), (255, 174, 66, 'Yellow Orange'), (255, 176, 172,
'Cornflower Lilac'), (255, 177, 179, 'Sundown'), (255, 179, 31, 'My Sin'),
(255, 181, 85, 'Texas Rose'), (255, 183, 213, 'Cotton Candy'), (255, 185, 123,
'Macaroni and Cheese'), (255, 186, 0, 'Selective Yellow'), (255, 189, 95,
'Koromiko'), (255, 191, 0, 'Amber'), (255, 192, 168, 'Wax Flower'), (255, 192,
203, 'Pink'), (255, 195, 192, 'Your Pink'), (255, 201, 1, 'Supernova'), (255,
203, 164, 'Flesh'), (255, 204, 51, 'Sunglow'), (255, 204, 92, 'Golden Tainoi'), 
(255, 204, 153, 'Peach Orange'), (255, 205, 140, 'Chardonnay'),
(255, 209, 220, 'Pastel Pink'), (255, 210, 183, 'Romantic'), (255, 211, 140,
'Grandis'), (255, 215, 0, 'Gold'), (255, 216, 0, 'School bus Yellow'), (255,
216, 217, 'Cosmos'), (255, 219, 88, 'Mustard'), (255, 220, 214, 'Peach Schnapps'), 
(255, 221, 175, 'Caramel'), (255, 221, 205, 'Tuft Bush'), (255,
221, 207, 'Watusi'), (255, 221, 244, 'Pink Lace'), (255, 222, 173, 'Navajo White'), 
(255, 222, 179, 'Frangipani'), (255, 225, 223, 'Pippin'), (255, 225,
242, 'Pale Rose'), (255, 226, 197, 'Negroni'), (255, 229, 160, 'Cream Brulee'), 
(255, 229, 180, 'Peach'), (255, 230, 199, 'Tequila'), (255, 231,
114, 'Kournikova'), (255, 234, 200, 'Sandy Beach'), (255, 234, 212, 'Karry'),
(255, 236, 19, 'Broom'), (255, 237, 188, 'Colonial White'), (255, 238, 216,
'Derby'), (255, 239, 161, 'Vis Vis'), (255, 239, 193, 'Egg White'), (255, 239,
213, 'Papaya Whip'), (255, 239, 236, 'Fair Pink'), (255, 240, 219, 'Peach Cream'), 
(255, 240, 245, 'Lavender blush'), (255, 241, 79, 'Gorse'), (255,
241, 181, 'Buttermilk'), (255, 241, 216, 'Pink Lady'), (255, 241, 238, 'Forget-me-not'), 
(255, 241, 249, 'Tutu'), (255, 243, 157, 'Picasso'), (255, 243, 241,
'Chardon'), (255, 244, 110, 'Paris Daisy'), (255, 244, 206, 'Barley White'),
(255, 244, 221, 'Egg Sour'), (255, 244, 224, 'Sazerac'), (255, 244, 232,
'Serenade'), (255, 244, 243, 'Chablis'), (255, 245, 238, 'Seashell Peach'),
(255, 245, 243, 'Sauvignon'), (255, 246, 212, 'Milk Punch'), (255, 246, 223,
'Varden'), (255, 246, 245, 'Rose White'), (255, 248, 209, 'Baja White'), (255,
249, 226, 'Gin Fizz'), (255, 249, 230, 'Early Dawn'), (255, 250, 205, 'Lemon Chiffon'), 
(255, 250, 244, 'Bridal Heath'), (255, 251, 220, 'Scotch Mist'),
(255, 251, 249, 'Soapstone'), (255, 252, 153, 'Witch Haze'), (255, 252, 234,
'Buttery White'), (255, 252, 238, 'Island Spice'), (255, 253, 208, 'Cream'),
(255, 253, 230, 'Chilean Heath'), (255, 253, 232, 'Travertine'), (255, 253,
243, 'Orchid White'), (255, 253, 244, 'Quarter Pearl Lusta'), (255, 254, 225,
'Half and Half'), (255, 254, 236, 'Apricot White'), (255, 254, 240, 'Rice Cake'), 
(255, 254, 246, 'Black White'), (255, 254, 253, 'Romance'), (255, 255,
0, 'Yellow'), (255, 255, 102, 'Laser Lemon'), (255, 255, 153, 'Pale Canary'),
(255, 255, 180, 'Portafino'), (255, 255, 240, 'Ivory'), (255, 255, 255,
'White'), (221, 72, 20, 'Ubuntu Original Orange'), (233, 84, 32, 'Ubuntu Orange')]


def rgb_to_lab(r, g, b):
    """Convert RGB colours to LAB colours
       thank you Roman Nazarkin, http://stackoverflow.com/a/16020102/1418014"""
    inputColor = [r, g, b]
    num = 0
    RGB = [0, 0, 0]
    for value in inputColor :
        value = float(value) / 255
        if value > 0.04045:
            value = ((value + 0.055) / 1.055 ) ** 2.4
        else:
            value = value / 12.92
        RGB[num] = value * 100
        num = num + 1
    XYZ = [0, 0, 0]
    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    XYZ[0] = float(XYZ[0]) / 95.047  # ref_X =  95.047   Observer= 2deg, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0   # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883 # ref_Z = 108.883

    num = 0
    for value in XYZ:
        if value > 0.008856:
            value = value ** (0.3333333333333333)
        else:
            value = (7.787 * value) + (16 / 116)
        XYZ[num] = value
        num = num + 1

    Lab = [0, 0, 0]
    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])

    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab

def deltaE(labA, labB):
    "deltaE is the standard way to compare two colours for how visibly alike they are"
    deltaL = labA[0] - labB[0]
    deltaA = labA[1] - labB[1]
    deltaB = labA[2] - labB[2]
    c1 = math.sqrt(labA[1] * labA[1] + labA[2] * labA[2])
    c2 = math.sqrt(labB[1] * labB[1] + labB[2] * labB[2])
    deltaC = c1 - c2;
    deltaH = deltaA * deltaA + deltaB * deltaB - deltaC * deltaC;
    if deltaH < 0:
        deltaH = 0
    else:
        deltaH = math.sqrt(deltaH);
    sc = 1.0 + 0.045 * c1;
    sh = 1.0 + 0.015 * c1;
    deltaLKlsl = deltaL / (1.0);
    deltaCkcsc = deltaC / (sc);
    deltaHkhsh = deltaH / (sh);
    i = deltaLKlsl * deltaLKlsl + deltaCkcsc * deltaCkcsc + deltaHkhsh * deltaHkhsh;
    if i < 0:
        return 0
    else:
        return math.sqrt(i)

LAB_COLOUR_NAMES = [(rgb_to_lab(x[0],x[1],x[2]), x[3]) for x in COLOUR_NAMES]

class Main(object):
    def __init__(self):
        # useful globals
        self.snapsize = (120, 120) # must both be even numbers, and must be square
        self.closest_name_cache = {}
        self.history = []
        self.colour_text_labels = []
        self.grabbed = False
        self.zoomlevel = 1
        GLib.set_application_name("Pick")

        # The CSS
        style_provider = Gtk.CssProvider()
        css = """
            GtkLabel { transition: 250ms ease-in-out; }
            GtkLabel.highlighted { background-color: rgba(255, 255, 0, 0.4); }
            GtkLabel#empty-heading { font-size: 200%; }
            GtkFrame {
                background-color: rgba(255, 255, 255, 0.6);
            }
            GtkEventBox GtkFrame {
                border-width: 0 0 1px 0;
                padding: 6px 0;
            }
            GtkEventBox:focused {
                background: rgba(0, 0, 0, 0.2);
            }
            GtkEventBox:nth-child(5) GtkFrame {
                border-width: 0;
                padding: 6px 0;
            }
        """
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # the window
        self.w = Gtk.Window()
        self.w.set_title("Pick")
        self.w.set_size_request((self.snapsize[0]/2) * 2 + 200, (self.snapsize[1]/2) * 5 + 200)
        self.w.connect("motion-notify-event", self.magnifier_move)
        self.w.connect("button-press-event", self.magnifier_clicked)
        self.w.connect("scroll-event", self.magnifier_scrollwheel)
        self.w.connect("key-press-event", self.magnifier_keypress)
        self.w.connect("destroy", Gtk.main_quit)

        devman = self.w.get_screen().get_display().get_device_manager()
        self.pointer = devman.get_client_pointer()
        keyboards = [x for x in devman.list_devices(Gdk.DeviceType.MASTER)
            if x.get_property("input-source") == Gdk.InputSource.KEYBOARD]
        self.keyboard = None
        if len(keyboards) > 0:
            self.keyboard = keyboards[0] # bit lairy, that, but it should be OK in normal use cases

        # The about dialog
        def show_about_dialog(*args):
            about_dialog = Gtk.AboutDialog()
            about_dialog.set_artists(["Sam Hewitt"])
            about_dialog.set_authors(["Stuart Langridge"])
            about_dialog.set_license_type(Gtk.License.MIT_X11)
            about_dialog.set_website("https://www.kryogenix.org/code/pick")
            about_dialog.run()
            if about_dialog: about_dialog.destroy()

        # The lowlight colour: used for subsidiary text throughout, and looked up from the theme
        ok, col = self.w.get_style_context().lookup_color("info_fg_color")
        if ok and False:
            self.lowlight_rgba = col
        else:
            self.lowlight_rgba = Gdk.RGBA(red=0.5, green=0.5, blue=0.5, alpha=1)

        # the headerbar
        head = Gtk.HeaderBar()
        head.set_show_close_button(True)
        head.props.title = "Pick"
        self.w.set_titlebar(head)
        btngrab = Gtk.Button()
        icon = Gio.ThemedIcon(name="pick-symbolic")
        theme_icon = Gtk.IconTheme.get_default().lookup_by_gicon(icon, 0, 0)
        if theme_icon:
            # our symbolic icon is included in the theme, so use it
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        else:
            # not in the theme, so we're probably running locally; use the local one
            image = Gtk.Image.new_from_file(os.path.join(os.path.split(__file__)[0], "..", 
                "data", "icons", "scalable", "apps", "pick-symbolic.svg"))
        btngrab.add(image)
        head.pack_start(btngrab)
        btngrab.connect("clicked", self.grab)

        # the box that contains everything
        self.vb = Gtk.VBox()

        # The menu
        action_group = Gtk.ActionGroup("menu_actions")
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)
        action_new = Gtk.Action("FileCapture", "_Capture",
            "Capture a pixel colour", Gtk.STOCK_NEW)
        action_new.connect("activate", self.grab)
        action_group.add_action_with_accel(action_new, None)
        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", Gtk.main_quit)
        action_group.add_action(action_filequit)
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpAbout", None, "About", None, None, show_about_dialog)
        ])
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string("""
            <ui>
              <menubar name='MenuBar'>
                <menu action='FileMenu'>
                  <menuitem action='FileCapture' />
                  <menuitem action='FileQuit' />
                </menu>
                <menu action='HelpMenu'>
                  <menuitem action='HelpAbout' />
                </menu>
              </menubar>
            </ui>""")
        accelgroup = uimanager.get_accel_group()
        self.w.add_accel_group(accelgroup)
        uimanager.insert_action_group(action_group)
        menubar = uimanager.get_widget("/MenuBar")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        self.vb.pack_start(box, False, False, 0)

        # the status bar and its formats list
        hb = Gtk.HBox()
        self.formatters = {
            "CSS hex": lambda r, g, b: "#%02x%02x%02x" % (r, g, b),
            "CSS uppercase hex": lambda r, g, b: ("#%02x%02x%02x" % (r, g, b)).upper(),
            "CSS rgb": lambda r, g, b: "rgb(%s, %s, %s)" % (r, g, b),
            "CSS rgba": lambda r, g, b: "rgba(%s, %s, %s, 1)" % (r, g, b),
            "GDK.RGBA": lambda r, g, b: "Gdk.RGBA(%.3f, %.3f, %.3f, 1.0)" % (r/255.0, g/255.0, b/255.0),
            "QML Qt.rgba": lambda r, g, b: "Qt.rgba(%.3f, %.3f, %.3f, 1.0)" % (r/255.0, g/255.0, b/255.0)
        }
        formats = Gtk.ListStore(str)
        for fr, fn in self.formatters.items():
            formats.append((fr,))
        self.fcom = Gtk.ComboBox.new_with_model(formats)
        fcell = Gtk.CellRendererText()
        self.fcom.pack_start(fcell, expand=True)
        self.fcom.add_attribute(fcell, "text", 0)
        vcell = Gtk.CellRendererText()
        self.fcom.pack_start(vcell, True)
        self.fcom.set_cell_data_func(vcell, self.formatRGB)
        vcell.set_property('xalign', 1.0)
        vcell.set_property("foreground_rgba", self.lowlight_rgba)
        self.active_formatter = "CSS rgb"
        self.fcom.set_active(self.formatters.keys().index(self.active_formatter))
        self.fcom.connect("changed", self.change_format)
        hb.pack_start(Gtk.Label("Format:"), False, False, 12)
        hb.pack_start(self.fcom, False, False, 12)
        self.vb.pack_start(hb, False, False, 12)

        # the box that history items go in
        hb3 = Gtk.HBox()
        f = Gtk.Frame()
        self.container_vb = Gtk.VBox()
        self.vb.pack_start(hb3, True, True, 0)
        hb3.pack_start(f, True, True, 12)
        f.add(self.container_vb)
        self.container_vb.get_style_context().add_class("container_vb")

        # The clear history button
        self.btnclear = Gtk.Button("Clear history")
        self.btnclear.set_sensitive(False)
        self.btnclear.connect("clicked", self.clear_history)
        hb2 = Gtk.HBox()
        hb2.pack_end(self.btnclear, False, False, 12)
        self.vb.pack_end(hb2, False, False, 12)

        # the empty state, which we always show now because we don't know if there is
        # history until we've loaded it, which is done lazily
        self.empty = Gtk.VBox()
        icon = Gio.ThemedIcon(name="pick")
        theme_icon = Gtk.IconTheme.get_default().lookup_by_gicon(icon, 0, 0)
        if theme_icon:
            # our symbolic icon is included in the theme, so use it
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG)
        else:
            # not in the theme, so we're probably running locally; use the local one
            image = Gtk.Image.new_from_file(os.path.join(os.path.split(__file__)[0], "..", 
                "data", "icons", "48x48", "apps", "pick.png"))
        image.set_property("valign", Gtk.Align.END)
        self.empty.pack_start(image, True, True, 0)
        nocol1 = Gtk.Label("No Colours")
        nocol1.set_name("empty-heading")
        self.empty.pack_start(nocol1, False, False, 12)
        nocol2 = Gtk.Label("You haven't picked any colours.")
        nocol2.set_property("valign", Gtk.Align.START)
        self.empty.pack_start(nocol2, True, True, 0)
        self.w.add(self.empty)

        # and, go
        self.w.show_all()
        GLib.idle_add(self.load_history)

    def clear_history(self, button):
        self.history = []
        for c in self.container_vb.get_children():
            c.get_parent().remove(c)
        self.w.remove(self.vb)
        self.w.add(self.empty)
        self.serialise()

    def grab(self, btn):
        self.grabbed = True
        self.w.iconify()
        # we grab the keyboard so that we get the Escape keypress to cancel a pick even though we're iconified
        if self.keyboard:
            self.keyboard.grab(
                self.w.get_window(),
                Gdk.GrabOwnership.APPLICATION,
                True,
                Gdk.EventMask.KEY_PRESS_MASK,
                None,
                Gdk.CURRENT_TIME)
        GLib.timeout_add(150, self.set_magnifier_cursor) # give the window time to iconify

    def set_magnifier_cursor(self):
        root = Gdk.get_default_root_window()
        pointer, px, py = self.pointer.get_position()

        # Screenshot where the cursor is, at snapsize
        self.latest_pb = self.snap(
            px-(self.snapsize[0]/2), py-(self.snapsize[1]/2), 
            self.snapsize[0], self.snapsize[1])

        # Zoom that screenshot up, and grab a snapsize-sized piece from the middle
        scaled_pb = self.latest_pb.scale_simple(
            self.snapsize[0] * 2, self.snapsize[1] * 2, GdkPixbuf.InterpType.NEAREST)
        scaled_pb_subset = scaled_pb.new_subpixbuf(
            self.snapsize[0] / 2 + 1, self.snapsize[1] / 2 + 1, self.snapsize[0], self.snapsize[1])

        # Create the base surface for our cursor
        base = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.snapsize[0] * self.zoomlevel, self.snapsize[1] * self.zoomlevel)
        base_context = cairo.Context(base)
        base_context.scale(self.zoomlevel, self.zoomlevel)

        # Create the circular path on our base surface
        base_context.arc(self.snapsize[0] / 2, self.snapsize[1] / 2, self.snapsize[0] / 2, 0, 2*math.pi)

        # Paste in the screenshot
        Gdk.cairo_set_source_pixbuf(base_context, scaled_pb_subset, 0, 0)

        # Save the context now, before clipping, so we can restore it later
        base_context.save()

        # Clip to that circular path, keeping the path around for later, and paint the pasted screenshot
        base_context.clip_preserve()
        base_context.paint()

        # set scale back for when we're drawing the borders
        base_context.scale(1, 1)

        # Draw the outside border of the magnifier
        base_context.set_source_rgba(0, 0, 0, 1)
        base_context.set_line_width(4)
        base_context.stroke()

        # Restore the context, thus removing the clip region
        base_context.restore()

        # Draw the inside square border of the magnifier
        base_context.set_source_rgba(255, 0, 0, 0.5)
        base_context.set_line_width(1)
        base_context.move_to(self.snapsize[0]/2 - 2, self.snapsize[1]/2 - 2)
        base_context.rel_line_to(3, 0)
        base_context.rel_line_to(0, 3)
        base_context.rel_line_to(-3, 0)
        base_context.rel_line_to(0, -3)
        base_context.stroke()

        # Get the current colour and write it on the magnifier, in the default font
        # with a black rectangle under it
        col = self.get_colour_from_pb(self.latest_pb)
        text = self.formatters[self.active_formatter](col[0], col[1], col[2])
        nfs = 9 + (1 * self.zoomlevel)
        if nfs > 14: nfs = 14
        base_context.set_font_size(nfs)
        x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = base_context.text_extents(text)
        text_draw_x = ((base.get_width() / self.zoomlevel) * 0.98) - text_width
        text_draw_y = ((base.get_height() / self.zoomlevel) * 0.95) - text_height
        rect_border_width = 2
        base_context.rectangle(
            text_draw_x - rect_border_width + x_bearing,
            text_draw_y - rect_border_width + y_bearing,
            text_width + (2 * rect_border_width),
            text_height + (2 * rect_border_width)
        )
        base_context.set_source_rgba(0, 0, 0, 0.7)
        base_context.fill()
        base_context.set_source_rgba(255, 255, 255, 1.0)
        base_context.move_to(text_draw_x, text_draw_y)
        base_context.show_text(text)

        # turn the base surface into a pixbuf and thence a cursor
        drawn_pb = Gdk.pixbuf_get_from_surface(base, 0, 0, base.get_width(), base.get_height())
        zoom_pb = drawn_pb.scale_simple(
            self.snapsize[0] * self.zoomlevel, self.snapsize[1] * self.zoomlevel, GdkPixbuf.InterpType.TILES)
        magnifier = Gdk.Cursor.new_from_pixbuf(
            self.w.get_screen().get_display(), 
            zoom_pb,
            zoom_pb.get_width()/2, zoom_pb.get_height()/2)

        # Set the cursor
        self.pointer.grab(
            self.w.get_window(),
            Gdk.GrabOwnership.APPLICATION,
            True,
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK,
            magnifier,
            Gdk.CURRENT_TIME)

    def ungrab(self, *args, **kwargs):
        self.pointer.ungrab(Gdk.CURRENT_TIME)
        if self.keyboard: self.keyboard.ungrab(Gdk.CURRENT_TIME)
        self.grabbed = False
        # deiconify doesn't seem to work, but http://stackoverflow.com/questions/24061029/how-to-deiconify-a-window-after-the-click-of-minimize-button-in-gtk
        self.w.deiconify()
        self.w.present()

    def get_cache_file(self):
        return os.path.join(GLib.get_user_cache_dir(), "colour-picker.json")

    def serialise(self, *args, **kwargs):
        # yeah, yeah, supposed to use Gio's async file stuff here. But it was writing
        # corrupted files, and I have no idea why; probably the Python var containing
        # the data was going out of scope or something. Anyway, we're only storing
        # five small images, so life's too short to hammer on this; we'll write with
        # Python and take the hit.
        fp = codecs.open(self.get_cache_file(), encoding="utf8", mode="w")
        json.dump({"colours": self.history, "formatter": self.active_formatter}, fp, indent=2)
        fp.close()

    def rounded_path(self, surface, w, h):
        radius = w / 10
        # https://www.cairographics.org/samples/rounded_rectangle/
        surface.arc(w - radius, radius, radius, -90 * math.pi / 180, 0)
        surface.arc(w - radius, h -radius, radius, 0, 90 * math.pi / 180)
        surface.arc(radius, h - radius, radius, 90 * math.pi / 180, 180 * math.pi / 180)
        surface.arc(radius, radius, radius, 180 * math.pi / 180, 270 * math.pi / 180)
        surface.close_path()

    def rectangle_draw(self, da, surface, r, g, b):
        w, h = da.get_size_request()
        self.rounded_path(surface, w, h)
        surface.set_source_rgb(r/255.0, g/255.0, b/255.0)
        surface.clip_preserve()
        surface.fill_preserve()
        surface.set_line_width(2)
        surface.set_source_rgba(0, 0, 0, 0.1)
        surface.stroke()

    def image_draw(self, da, surface, pixbuf):
        w, h = da.get_size_request()
        self.rounded_path(surface, w, h)
        Gdk.cairo_set_source_pixbuf(surface, pixbuf, 0, 0);
        surface.clip_preserve()
        surface.paint()
        surface.set_line_width(2)
        surface.set_source_rgba(0, 0, 0, 0.1)
        surface.stroke()

    def add_history_item(self, r, g, b, base64_imgdata=None, pixbuf=None):
        def show_copy(eb, ev, img): img.set_opacity(1)
        def hide_copy(eb, ev, img): img.set_opacity(0)
        def clipboard(button, r, g, b, label):
            def unfade(label):
                label.get_style_context().remove_class("highlighted")
            colour = self.formatters[self.active_formatter](r, g, b)
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(colour, len(colour))
            label.get_style_context().add_class("highlighted")
            GLib.timeout_add(300, unfade, label)

        eb = Gtk.EventBox()
        hb = Gtk.HBox()
        f = Gtk.Frame()
        eb.add(f)
        f.add(hb)

        if base64_imgdata:
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(base64_imgdata.decode("base64"))
            pixbuf = loader.get_pixbuf()
            loader.close()
        elif pixbuf:
            success, data = pixbuf.save_to_bufferv("png", [], [])
            base64_imgdata = data.encode("base64")
        else:
            raise Exception("A history item must have either imgdata or a pixbuf")

        i = Gtk.DrawingArea()
        i.set_size_request(self.snapsize[0]/2, self.snapsize[1]/2)
        i.connect("draw", self.image_draw, pixbuf)
        hb.pack_start(i, False, False, 6)

        area = Gtk.DrawingArea()
        area.set_size_request(self.snapsize[0]/2, self.snapsize[1]/2)
        area.connect("draw", self.rectangle_draw, r, g, b)
        hb.pack_start(area, False, False, 6)

        lbl = Gtk.Label()
        self.colour_text_labels.append(lbl)
        self.set_colour_label_text(lbl, r, g, b)
        lbl.set_halign(Gtk.Align.START)
        hb.pack_start(lbl, True, True, 6)

        copy = Gtk.Button.new_from_icon_name("edit-copy-symbolic", 0)
        copy.set_label("Copy")
        copy.set_opacity(0)
        copy.connect("clicked", clipboard, r, g, b, lbl)
        copy.connect("enter-notify-event", show_copy, copy)
        copy.connect("leave-notify-event", hide_copy, copy)
        hb.pack_start(copy, False, False, 6)

        eb.connect("enter-notify-event", show_copy, copy)
        eb.connect("leave-notify-event", hide_copy, copy)
        #eb.connect("button-press-event", clipboard, r, g, b)
        eb.set_tooltip_text("Copy to clipboard")

        eb.set_property("can_focus", True)
        eb.connect("focus-in-event", show_copy, copy)
        eb.connect("focus-out-event", hide_copy, copy)

        self.container_vb.pack_start(eb, False, False, 0)
        self.container_vb.reorder_child(eb, 0)
        self.vb.show_all()
        eb.show_all()

        self.history.append({
            "imgdata": base64_imgdata,
            "colour": [r, g, b]
        })

        while len(self.history) > 5:
            del self.history[0]
            del self.colour_text_labels[0]
            self.container_vb.get_children()[5].destroy()

        if self.empty.get_parent():
            self.empty.get_parent().remove(self.empty)
        if not self.vb.get_parent():
            self.w.add(self.vb)
            self.vb.show_all()
        self.btnclear.set_sensitive(True)

    def set_colour_label_text(self, lbl, r, g, b):
        lbl.set_markup('%s\n<span color="%s">%s</span>' % (
            self.closest_name(r, g, b),
            self.formatters["CSS hex"](
                255 * self.lowlight_rgba.red,
                255 * self.lowlight_rgba.green,
                255 * self.lowlight_rgba.blue),
            self.formatters[self.active_formatter](r, g, b)
        ))

    def finish_loading_history(self, f, res):
        try:
            success, contents, _ = f.load_contents_finish(res)
            data = json.loads(contents)
            colours = data["colours"]
            for item in colours:
                self.add_history_item(
                    item["colour"][0], item["colour"][1], item["colour"][2],
                    base64_imgdata=item["imgdata"]
                )
            f = data.get("formatter")
            if f and f in self.formatters.keys():
                self.active_formatter = f
                self.fcom.set_active(self.formatters.keys().index(f))
        except:
            #print "Failed to restore data"
            raise

    def load_history(self):
        f = Gio.File.new_for_path(self.get_cache_file())
        f.load_contents_async(None, self.finish_loading_history)

    def magnifier_scrollwheel(self, window, ev):
        if self.grabbed:
            if ev.direction == Gdk.ScrollDirection.SMOOTH:
                return
            if ev.direction == Gdk.ScrollDirection.UP:
                self.zoomlevel += 1
            elif ev.direction == Gdk.ScrollDirection.DOWN:
                self.zoomlevel -= 1
                if self.zoomlevel < 1:
                    self.zoomlevel = 1
            else:
                return
            self.set_magnifier_cursor()

    def magnifier_keypress(self, window, ev):
        if self.grabbed:
            if ev.keyval == Gdk.KEY_Escape:
                self.ungrab()

    def magnifier_clicked(self, window, ev):
        if self.grabbed:
            self.ungrab()
            if ev.button != 1: return # if this is not the primary button, bail
            colour = self.get_colour_from_pb(self.latest_pb)
            pbcopy = self.latest_pb.scale_simple(self.snapsize[0] / 2,
                self.snapsize[1] / 2, GdkPixbuf.InterpType.TILES)
            self.add_history_item(colour[0], colour[1], colour[2], pixbuf=pbcopy)
            GLib.idle_add(self.serialise)

    def get_colour_from_pb(self, pb):
        pixel_data = pb.get_pixels()
        offset = (pb.get_rowstride() * (self.snapsize[1] / 2)) + ((self.latest_pb.get_rowstride() / self.snapsize[0]) * (self.snapsize[0] / 2))
        rgb_vals = tuple([ord(x) for x in pixel_data[offset:offset+3]])
        return rgb_vals

    def magnifier_move(self, *args, **kwargs):
        if not self.grabbed: return
        self.set_magnifier_cursor()

    def change_format(self, cb):
        self.active_formatter = cb.get_model().get_value(cb.get_active_iter(), 0)
        for lbl, hist in zip(self.colour_text_labels, self.history):
            self.set_colour_label_text(lbl, hist["colour"][0], hist["colour"][1], hist["colour"][2])
        GLib.idle_add(self.serialise)

    def closest_name(self, r, g, b):
        max_deltaE_found = 999999999
        col = self.closest_name_cache.get((r, g, b))
        if col is not None: return col
        labcol = rgb_to_lab(r, g, b)
        for reflabcol, name in LAB_COLOUR_NAMES:
            dE = deltaE(labcol, reflabcol)
            if dE < max_deltaE_found:
                col = name
                max_deltaE_found = dE
        self.closest_name_cache[(r, g, b)] = col
        return col

    def formatRGB(self, column, cell_renderer, model, iter):
        formatter = self.formatters.get(model.get_value(iter, 0))
        text = "?"
        if formatter:
            text = formatter(255, 255, 255)
        cell_renderer.set_property("text", text)

    def snap(self, x, y, w, h):
        display=Gdk.Display.get_default()
        (screen,self.x,self.y,modifier) = display.get_pointer()
        root = Gdk.get_default_root_window()
        screenshot = Gdk.pixbuf_get_from_window(root, x, y, w, h)
        return screenshot

def main():
    Main()
    Gtk.main()

if __name__ == "__main__": main()


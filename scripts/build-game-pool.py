#!/usr/bin/env python3
"""Build the "Who Painted It?" game pool from open-access museum APIs.

Sources (public-domain / CC0 records only, decided by each museum's own flag):
  - The Metropolitan Museum of Art — Collection API v1.1 search + v1 objects
    (object.isPublicDomain must be true; artist from object.artistDisplayName)
  - Art Institute of Chicago — the museum's official open data dump
    (https://artic-api-data.s3.amazonaws.com/artic-api-data.tar.bz2, the same
    records its API serves; is_public_domain must be true; artist_title).
    The live AIC API is behind a bot wall from some networks; the dump is the
    museum's own sanctioned bulk route to the identical data.
  - The Cleveland Museum of Art — Open Access API (cc0=1 filter;
    artist from the record's creators list).

Attribution rule: a work enters the pool only when the museum's own record
for that exact object names the artist, and the name matches a roster alias.
No image is ever attached to an artist/title by inference.

Levels are curatorial: a hand list of canonical works is pinned to levels
1-3; everything else is banded by the artist's fame tier (see POOL.md).
Output: public/data/game/pool.json (+ prints a per-level summary).
"""
import bz2
import hashlib
import io
import json
import re
import sys
import tarfile
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = __file__.rsplit('/scripts/', 1)[0]
OUT = ROOT + '/public/data/game/pool.json'
AIC_TARBALL = '/tmp/artic-api-data.tar.bz2'
UA = {'User-Agent': 'ArtistResearchAtlas game-pool builder (open-access research)'}

# ---------------------------------------------------------------- roster
# (name, aliases, birth, death, floruit century, movement, nationality,
#  circle, fame tier 1=household name .. 4=specialist)
ROSTER = [
    # --- Impressionist circle
    ("Claude Monet", "claude monet", 1840, 1926, 19, "Impressionism", "French", "impressionists", 1),
    ("Pierre-Auguste Renoir", "pierre auguste renoir|renoir", 1841, 1919, 19, "Impressionism", "French", "impressionists", 1),
    ("Edgar Degas", "edgar degas|degas", 1834, 1917, 19, "Impressionism", "French", "impressionists", 1),
    ("Édouard Manet", "edouard manet|manet", 1832, 1883, 19, "Realism", "French", "impressionists", 1),
    ("Camille Pissarro", "camille pissarro|pissarro", 1830, 1903, 19, "Impressionism", "French", "impressionists", 2),
    ("Berthe Morisot", "berthe morisot|morisot", 1841, 1895, 19, "Impressionism", "French", "impressionists", 2),
    ("Mary Cassatt", "mary cassatt|cassatt", 1844, 1926, 19, "Impressionism", "American", "impressionists", 2),
    ("Gustave Caillebotte", "gustave caillebotte|caillebotte", 1848, 1894, 19, "Impressionism", "French", "impressionists", 2),
    ("Alfred Sisley", "alfred sisley|sisley", 1839, 1899, 19, "Impressionism", "British", "impressionists", 3),
    ("Frédéric Bazille", "frederic bazille|bazille", 1841, 1870, 19, "Impressionism", "French", "impressionists", 3),
    ("Armand Guillaumin", "armand guillaumin|guillaumin", 1841, 1927, 19, "Impressionism", "French", "impressionists", 4),
    ("Johan Barthold Jongkind", "johan barthold jongkind|jongkind", 1819, 1891, 19, "Impressionism", "Dutch", "impressionists", 4),
    # --- Post-Impressionist circle
    ("Vincent van Gogh", "vincent van gogh|van gogh", 1853, 1890, 19, "Post-Impressionism", "Dutch", "post-impressionists", 1),
    ("Paul Gauguin", "paul gauguin|gauguin", 1848, 1903, 19, "Post-Impressionism", "French", "post-impressionists", 1),
    ("Paul Cézanne", "paul cezanne|cezanne", 1839, 1906, 19, "Post-Impressionism", "French", "post-impressionists", 1),
    ("Georges Seurat", "georges seurat|seurat", 1859, 1891, 19, "Neo-Impressionism", "French", "post-impressionists", 1),
    ("Henri de Toulouse-Lautrec", "henri de toulouse lautrec|toulouse lautrec", 1864, 1901, 19, "Post-Impressionism", "French", "post-impressionists", 2),
    ("Henri Rousseau", "henri rousseau|rousseau", 1844, 1910, 19, "Post-Impressionism", "French", "post-impressionists", 2),
    ("Paul Signac", "paul signac|signac", 1863, 1935, 19, "Neo-Impressionism", "French", "post-impressionists", 3),
    ("Odilon Redon", "odilon redon|redon", 1840, 1916, 19, "Symbolism", "French", "post-impressionists", 3),
    ("Pierre Bonnard", "pierre bonnard|bonnard", 1867, 1947, 20, "Post-Impressionism", "French", "post-impressionists", 3),
    ("Édouard Vuillard", "edouard vuillard|vuillard", 1868, 1940, 20, "Post-Impressionism", "French", "post-impressionists", 3),
    ("Edvard Munch", "edvard munch|munch", 1863, 1944, 19, "Symbolism", "Norwegian", "post-impressionists", 2),
    ("Maurice Denis", "maurice denis", 1870, 1943, 20, "Post-Impressionism", "French", "post-impressionists", 4),
    ("Félix Vallotton", "felix vallotton|vallotton", 1865, 1925, 19, "Post-Impressionism", "Swiss", "post-impressionists", 4),
    ("Henri-Edmond Cross", "henri edmond cross", 1856, 1910, 19, "Neo-Impressionism", "French", "post-impressionists", 4),
    ("Maximilien Luce", "maximilien luce|luce", 1858, 1941, 19, "Neo-Impressionism", "French", "post-impressionists", 4),
    # --- Dutch Golden Age
    ("Rembrandt van Rijn", "rembrandt van rijn|rembrandt harmensz van rijn|rembrandt", 1606, 1669, 17, "Baroque", "Dutch", "dutch-golden", 1),
    ("Johannes Vermeer", "johannes vermeer|vermeer", 1632, 1675, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 1),
    ("Frans Hals", "frans hals", 1582, 1666, 17, "Baroque", "Dutch", "dutch-golden", 2),
    ("Jan Steen", "jan steen", 1626, 1679, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 2),
    ("Jacob van Ruisdael", "jacob van ruisdael|jacob ruisdael", 1628, 1682, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 2),
    ("Meindert Hobbema", "meindert hobbema|hobbema", 1638, 1709, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 3),
    ("Aelbert Cuyp", "aelbert cuyp|cuyp", 1620, 1691, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 3),
    ("Pieter de Hooch", "pieter de hooch|de hooch", 1629, 1684, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 3),
    ("Gerard ter Borch", "gerard ter borch|ter borch", 1617, 1681, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 4),
    ("Gabriel Metsu", "gabriel metsu|metsu", 1629, 1667, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 4),
    ("Gerard Dou", "gerard dou|gerrit dou", 1613, 1675, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 4),
    ("Adriaen van Ostade", "adriaen van ostade|van ostade", 1610, 1685, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 4),
    ("Salomon van Ruysdael", "salomon van ruysdael|salomon van ruisdael", 1602, 1670, 17, "Dutch Golden Age", "Dutch", "dutch-golden", 4),
    # --- Flemish Baroque
    ("Peter Paul Rubens", "peter paul rubens|rubens", 1577, 1640, 17, "Baroque", "Flemish", "flemish-baroque", 1),
    ("Anthony van Dyck", "anthony van dyck|antoon van dyck|van dyck", 1599, 1641, 17, "Baroque", "Flemish", "flemish-baroque", 2),
    ("Jacob Jordaens", "jacob jordaens|jordaens", 1593, 1678, 17, "Baroque", "Flemish", "flemish-baroque", 3),
    ("Jan Brueghel the Elder", "jan brueghel the elder|jan bruegel the elder", 1568, 1625, 17, "Baroque", "Flemish", "flemish-baroque", 3),
    ("Frans Snyders", "frans snyders|snyders", 1579, 1657, 17, "Baroque", "Flemish", "flemish-baroque", 4),
    ("David Teniers the Younger", "david teniers the younger|david teniers", 1610, 1690, 17, "Baroque", "Flemish", "flemish-baroque", 4),
    ("Clara Peeters", "clara peeters|peeters", 1594, 1657, 17, "Baroque", "Flemish", "flemish-baroque", 4),
    ("Jan Brueghel the Younger", "jan brueghel the younger|jan bruegel the younger", 1601, 1678, 17, "Baroque", "Flemish", "flemish-baroque", 4),
    # --- Italian Renaissance
    ("Sandro Botticelli", "sandro botticelli|botticelli", 1445, 1510, 15, "Renaissance", "Italian", "italian-renaissance", 1),
    ("Leonardo da Vinci", "leonardo da vinci|leonardo", 1452, 1519, 15, "Renaissance", "Italian", "italian-renaissance", 1),
    ("Raphael", "raphael|raffaello santi|raffaello sanzio", 1483, 1520, 16, "Renaissance", "Italian", "italian-renaissance", 1),
    ("Michelangelo", "michelangelo|michelangelo buonarroti", 1475, 1564, 16, "Renaissance", "Italian", "italian-renaissance", 1),
    ("Titian", "titian|tiziano vecellio", 1488, 1576, 16, "Renaissance", "Italian", "italian-renaissance", 1),
    ("Tintoretto", "tintoretto|jacopo robusti", 1518, 1594, 16, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Paolo Veronese", "paolo veronese|veronese|paolo caliari", 1528, 1588, 16, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Andrea Mantegna", "andrea mantegna|mantegna", 1431, 1506, 15, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Giovanni Bellini", "giovanni bellini", 1430, 1516, 15, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Fra Angelico", "fra angelico|guido di pietro", 1395, 1455, 15, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Piero della Francesca", "piero della francesca", 1415, 1492, 15, "Renaissance", "Italian", "italian-renaissance", 2),
    ("Domenico Ghirlandaio", "domenico ghirlandaio|ghirlandaio", 1448, 1494, 15, "Renaissance", "Italian", "italian-renaissance", 3),
    ("Perugino", "perugino|pietro perugino|pietro vannucci", 1446, 1523, 15, "Renaissance", "Italian", "italian-renaissance", 3),
    ("Correggio", "correggio|antonio da correggio|antonio allegri", 1489, 1534, 16, "Renaissance", "Italian", "italian-renaissance", 3),
    ("Giorgione", "giorgione|giorgio barbarelli", 1477, 1510, 16, "Renaissance", "Italian", "italian-renaissance", 3),
    ("Parmigianino", "parmigianino|francesco mazzola", 1503, 1540, 16, "Renaissance", "Italian", "italian-renaissance", 4),
    ("Andrea del Sarto", "andrea del sarto", 1486, 1530, 16, "Renaissance", "Italian", "italian-renaissance", 4),
    ("Pontormo", "pontormo|jacopo pontormo", 1494, 1557, 16, "Renaissance", "Italian", "italian-renaissance", 4),
    ("Lorenzo Lotto", "lorenzo lotto|lotto", 1480, 1557, 16, "Renaissance", "Italian", "italian-renaissance", 4),
    # --- Northern Renaissance
    ("Albrecht Dürer", "albrecht durer|durer", 1471, 1528, 16, "Northern Renaissance", "German", "northern-renaissance", 1),
    ("Jan van Eyck", "jan van eyck|van eyck", 1390, 1441, 15, "Northern Renaissance", "Flemish", "northern-renaissance", 1),
    ("Hans Holbein the Younger", "hans holbein the younger|hans holbein|holbein", 1497, 1543, 16, "Northern Renaissance", "German", "northern-renaissance", 2),
    ("Lucas Cranach the Elder", "lucas cranach the elder|lucas cranach|cranach", 1472, 1553, 16, "Northern Renaissance", "German", "northern-renaissance", 2),
    ("Rogier van der Weyden", "rogier van der weyden|van der weyden", 1399, 1464, 15, "Northern Renaissance", "Flemish", "northern-renaissance", 2),
    ("Hieronymus Bosch", "hieronymus bosch|bosch", 1450, 1516, 15, "Northern Renaissance", "Dutch", "northern-renaissance", 2),
    ("Pieter Brueghel the Elder", "pieter brueghel the elder|pieter bruegel the elder", 1525, 1569, 16, "Northern Renaissance", "Flemish", "northern-renaissance", 2),
    ("Albrecht Altdorfer", "albrecht altdorfer|altdorfer", 1480, 1538, 16, "Northern Renaissance", "German", "northern-renaissance", 3),
    ("Hans Memling", "hans memling|memling", 1430, 1494, 15, "Northern Renaissance", "Flemish", "northern-renaissance", 3),
    ("Joachim Patinir", "joachim patinir|patinir", 1480, 1524, 16, "Northern Renaissance", "Flemish", "northern-renaissance", 4),
    ("Quinten Massys", "quenten massys|quentin massys|massys", 1466, 1530, 16, "Northern Renaissance", "Flemish", "northern-renaissance", 4),
    ("Martin Schongauer", "martin schongauer|schongauer", 1445, 1491, 15, "Northern Renaissance", "German", "northern-renaissance", 4),
    # --- Roman Baroque / classicism
    ("Caravaggio", "caravaggio|michelangelo merisi da caravaggio", 1571, 1610, 17, "Baroque", "Italian", "roman-baroque", 1),
    ("Artemisia Gentileschi", "artemisia gentileschi|gentileschi", 1593, 1653, 17, "Baroque", "Italian", "roman-baroque", 2),
    ("Nicolas Poussin", "nicolas poussin|poussin", 1594, 1665, 17, "Baroque", "French", "roman-baroque", 2),
    ("Claude Lorrain", "claude lorrain|claude gellee|claude", 1600, 1682, 17, "Baroque", "French", "roman-baroque", 2),
    ("Guido Reni", "guido reni|reni", 1575, 1642, 17, "Baroque", "Italian", "roman-baroque", 3),
    ("Guercino", "guercino|giovanni francesco barbieri", 1591, 1666, 17, "Baroque", "Italian", "roman-baroque", 3),
    ("Salvator Rosa", "salvator rosa", 1615, 1673, 17, "Baroque", "Italian", "roman-baroque", 4),
    # --- Spanish masters
    ("Diego Velázquez", "diego velazquez|velazquez", 1599, 1660, 17, "Baroque", "Spanish", "spanish-masters", 1),
    ("El Greco", "el greco|domenikos theotokopoulos", 1541, 1614, 16, "Renaissance", "Greek", "spanish-masters", 1),
    ("Francisco Goya", "francisco goya|francisco de goya|goya", 1746, 1828, 18, "Romanticism", "Spanish", "spanish-masters", 1),
    ("Bartolomé Esteban Murillo", "bartolome esteban murillo|murillo", 1617, 1682, 17, "Baroque", "Spanish", "spanish-masters", 2),
    ("Francisco de Zurbarán", "francisco de zurbaran|zurbaran", 1598, 1664, 17, "Baroque", "Spanish", "spanish-masters", 2),
    ("Jusepe de Ribera", "jusepe de ribera|ribera", 1591, 1652, 17, "Baroque", "Spanish", "spanish-masters", 3),
    ("Joaquín Sorolla", "joaquin sorolla|sorolla", 1863, 1923, 19, "Impressionism", "Spanish", "spanish-masters", 3),
    ("Alonso Cano", "alonso cano|cano", 1601, 1667, 17, "Baroque", "Spanish", "spanish-masters", 4),
    # --- Barbizon & Realists
    ("Gustave Courbet", "gustave courbet|courbet", 1819, 1877, 19, "Realism", "French", "barbizon-realists", 1),
    ("Jean-Baptiste-Camille Corot", "jean baptiste camille corot|corot", 1796, 1875, 19, "Barbizon", "French", "barbizon-realists", 2),
    ("Jean-François Millet", "jean francois millet|millet", 1814, 1875, 19, "Realism", "French", "barbizon-realists", 2),
    ("Honoré Daumier", "honore daumier|daumier", 1808, 1879, 19, "Realism", "French", "barbizon-realists", 2),
    ("Théodore Rousseau", "theodore rousseau", 1812, 1867, 19, "Barbizon", "French", "barbizon-realists", 3),
    ("Henri Fantin-Latour", "henri fantin latour|fantin latour", 1836, 1904, 19, "Realism", "French", "barbizon-realists", 3),
    ("Charles-François Daubigny", "charles francois daubigny|daubigny", 1817, 1878, 19, "Barbizon", "French", "barbizon-realists", 3),
    ("Narcisse Virgilio Díaz de la Peña", "narcisse virgilio diaz de la pena|narcisse diaz de la pena|diaz de la pena", 1807, 1876, 19, "Barbizon", "French", "barbizon-realists", 4),
    ("Jules Dupré", "jules dupre|dupre", 1811, 1889, 19, "Barbizon", "French", "barbizon-realists", 4),
    ("Constant Troyon", "constant troyon|troyon", 1810, 1865, 19, "Barbizon", "French", "barbizon-realists", 4),
    # --- British classics
    ("John Constable", "john constable|constable", 1776, 1837, 19, "Romanticism", "British", "british-classics", 1),
    ("J.M.W. Turner", "joseph mallord william turner|j m w turner|turner", 1775, 1851, 19, "Romanticism", "British", "british-classics", 1),
    ("Thomas Gainsborough", "thomas gainsborough|gainsborough", 1727, 1788, 18, "British School", "British", "british-classics", 2),
    ("Joshua Reynolds", "joshua reynolds|reynolds", 1723, 1792, 18, "British School", "British", "british-classics", 2),
    ("William Hogarth", "william hogarth|hogarth", 1697, 1764, 18, "British School", "British", "british-classics", 2),
    ("George Stubbs", "george stubbs|stubbs", 1724, 1806, 18, "British School", "British", "british-classics", 3),
    ("Thomas Lawrence", "thomas lawrence", 1769, 1830, 18, "British School", "British", "british-classics", 3),
    ("Joseph Wright of Derby", "joseph wright of derby|wright of derby", 1734, 1797, 18, "British School", "British", "british-classics", 3),
    ("John Singleton Copley", "john singleton copley|copley", 1738, 1815, 18, "British School", "American", "british-classics", 3),
    ("Gilbert Stuart", "gilbert stuart|stuart", 1755, 1828, 18, "British School", "American", "british-classics", 3),
    ("George Romney", "george romney|romney", 1734, 1802, 18, "British School", "British", "british-classics", 4),
    ("Henry Raeburn", "henry raeburn|raeburn", 1756, 1823, 18, "British School", "Scottish", "british-classics", 4),
    # --- Pre-Raphaelites & Victorians
    ("Dante Gabriel Rossetti", "dante gabriel rossetti|rossetti", 1828, 1882, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 2),
    ("John Everett Millais", "john everett millais|millais", 1829, 1896, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 2),
    ("William Holman Hunt", "william holman hunt|holman hunt", 1827, 1910, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 3),
    ("Edward Burne-Jones", "edward burne jones|burne jones", 1833, 1898, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 3),
    ("John William Waterhouse", "john william waterhouse|waterhouse", 1849, 1917, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 3),
    ("Frederic Leighton", "frederic leighton|leighton", 1830, 1896, 19, "Academic", "British", "pre-raphaelites", 3),
    ("Lawrence Alma-Tadema", "lawrence alma tadema|alma tadema", 1836, 1912, 19, "Academic", "Dutch", "pre-raphaelites", 3),
    ("Ford Madox Brown", "ford madox brown", 1821, 1893, 19, "Pre-Raphaelitism", "British", "pre-raphaelites", 4),
    # --- American 19th century
    ("Winslow Homer", "winslow homer|homer", 1836, 1910, 19, "American Realism", "American", "american-19th", 1),
    ("John Singer Sargent", "john singer sargent|sargent", 1856, 1925, 19, "Realism", "American", "american-19th", 1),
    ("Thomas Cole", "thomas cole", 1801, 1848, 19, "Hudson River School", "American", "american-19th", 2),
    ("Frederic Edwin Church", "frederic edwin church|frederick edwin church|church", 1826, 1900, 19, "Hudson River School", "American", "american-19th", 2),
    ("Albert Bierstadt", "albert bierstadt|bierstadt", 1830, 1902, 19, "Hudson River School", "American", "american-19th", 2),
    ("Thomas Eakins", "thomas eakins|eakins", 1844, 1916, 19, "American Realism", "American", "american-19th", 2),
    ("James McNeill Whistler", "james mcneill whistler|james abbott mcneill whistler|whistler", 1834, 1903, 19, "Tonalism", "American", "american-19th", 2),
    ("Thomas Moran", "thomas moran|moran", 1837, 1926, 19, "Hudson River School", "American", "american-19th", 3),
    ("John Frederick Kensett", "john frederick kensett|kensett", 1816, 1872, 19, "Hudson River School", "American", "american-19th", 3),
    ("Martin Johnson Heade", "martin johnson heade|heade", 1819, 1904, 19, "Luminism", "American", "american-19th", 3),
    ("George Inness", "george inness|inness", 1825, 1894, 19, "Tonalism", "American", "american-19th", 3),
    ("William Merritt Chase", "william merritt chase|chase", 1849, 1916, 19, "American Impressionism", "American", "american-19th", 3),
    ("Childe Hassam", "childe hassam|hassam", 1859, 1935, 19, "American Impressionism", "American", "american-19th", 3),
    ("Sanford Robinson Gifford", "sanford robinson gifford|gifford", 1823, 1880, 19, "Hudson River School", "American", "american-19th", 4),
    ("Jasper Francis Cropsey", "jasper francis cropsey|cropsey", 1823, 1900, 19, "Hudson River School", "American", "american-19th", 4),
    ("Fitz Henry Lane", "fitz henry lane|fitz hugh lane|lane", 1804, 1865, 19, "Luminism", "American", "american-19th", 4),
    ("Eastman Johnson", "eastman johnson", 1824, 1906, 19, "American Realism", "American", "american-19th", 4),
    ("John Henry Twachtman", "john henry twachtman|twachtman", 1853, 1902, 19, "American Impressionism", "American", "american-19th", 4),
    ("J. Alden Weir", "j alden weir|julian alden weir|weir", 1852, 1919, 19, "American Impressionism", "American", "american-19th", 4),
    ("Cecilia Beaux", "cecilia beaux|beaux", 1855, 1942, 19, "American Impressionism", "American", "american-19th", 4),
    # --- French academic & symbolist
    ("William-Adolphe Bouguereau", "william adolphe bouguereau|bouguereau", 1825, 1905, 19, "Academic", "French", "french-academic", 2),
    ("Gustave Moreau", "gustave moreau|moreau", 1826, 1898, 19, "Symbolism", "French", "french-academic", 3),
    ("Pierre Puvis de Chavannes", "pierre puvis de chavannes|puvis de chavannes", 1824, 1898, 19, "Symbolism", "French", "french-academic", 3),
    ("Jean-Léon Gérôme", "jean leon gerome|gerome", 1824, 1904, 19, "Academic", "French", "french-academic", 3),
    ("Alexandre Cabanel", "alexandre cabanel|cabanel", 1823, 1889, 19, "Academic", "French", "french-academic", 4),
    ("Jules Breton", "jules breton|breton", 1827, 1906, 19, "Realism", "French", "french-academic", 4),
    ("Léon Bonnat", "leon bonnat|bonnat", 1833, 1922, 19, "Academic", "French", "french-academic", 4),
    # --- French Rococo & 18th century
    ("Antoine Watteau", "antoine watteau|watteau", 1684, 1721, 18, "Rococo", "French", "french-rococo", 2),
    ("François Boucher", "francois boucher|boucher", 1703, 1770, 18, "Rococo", "French", "french-rococo", 2),
    ("Jean-Honoré Fragonard", "jean honore fragonard|fragonard", 1732, 1806, 18, "Rococo", "French", "french-rococo", 2),
    ("Jean-Baptiste-Siméon Chardin", "jean baptiste simeon chardin|chardin", 1699, 1779, 18, "Rococo", "French", "french-rococo", 2),
    ("Jean-Baptiste Greuze", "jean baptiste greuze|greuze", 1725, 1805, 18, "Rococo", "French", "french-rococo", 3),
    ("Élisabeth Louise Vigée Le Brun", "elisabeth louise vigee le brun|vigee le brun", 1755, 1842, 18, "Rococo", "French", "french-rococo", 3),
    ("Nicolas Lancret", "nicolas lancret|lancret", 1690, 1743, 18, "Rococo", "French", "french-rococo", 4),
    ("Jean-Baptiste Pater", "jean baptiste pater|pater", 1695, 1736, 18, "Rococo", "French", "french-rococo", 4),
    ("Maurice-Quentin de La Tour", "maurice quentin de la tour|quentin de la tour|la tour", 1704, 1788, 18, "Rococo", "French", "french-rococo", 4),
    # --- Venetian 18th century
    ("Giovanni Battista Tiepolo", "giovanni battista tiepolo|gianbattista tiepolo|tiepolo", 1696, 1770, 18, "Venetian School", "Italian", "venetian-18th", 2),
    ("Canaletto", "canaletto|giovanni antonio canal", 1697, 1768, 18, "Venetian School", "Italian", "venetian-18th", 2),
    ("Francesco Guardi", "francesco guardi|guardi", 1712, 1793, 18, "Venetian School", "Italian", "venetian-18th", 3),
    ("Bernardo Bellotto", "bernardo bellotto|bellotto", 1721, 1780, 18, "Venetian School", "Italian", "venetian-18th", 3),
    ("Giovanni Paolo Panini", "giovanni paolo panini|panini", 1691, 1765, 18, "Venetian School", "Italian", "venetian-18th", 4),
    # --- Neoclassicism & Romanticism
    ("Jacques-Louis David", "jacques louis david|david", 1748, 1825, 18, "Neoclassicism", "French", "romantic-neoclassical", 1),
    ("Jean-Auguste-Dominique Ingres", "jean auguste dominique ingres|ingres", 1780, 1867, 19, "Neoclassicism", "French", "romantic-neoclassical", 1),
    ("Eugène Delacroix", "eugene delacroix|delacroix", 1798, 1863, 19, "Romanticism", "French", "romantic-neoclassical", 1),
    ("Théodore Géricault", "theodore gericault|gericault", 1791, 1824, 19, "Romanticism", "French", "romantic-neoclassical", 2),
    ("Caspar David Friedrich", "caspar david friedrich|friedrich", 1774, 1840, 19, "Romanticism", "German", "romantic-neoclassical", 2),
    ("Angelica Kauffmann", "angelica kauffmann|kauffmann", 1741, 1807, 18, "Neoclassicism", "Swiss", "romantic-neoclassical", 3),
    ("Benjamin West", "benjamin west|west", 1738, 1820, 18, "Neoclassicism", "American", "romantic-neoclassical", 3),
    ("Anne-Louis Girodet", "anne louis girodet|girodet", 1767, 1824, 18, "Neoclassicism", "French", "romantic-neoclassical", 4),
    ("Antoine-Jean Gros", "antoine jean gros|gros", 1771, 1835, 18, "Neoclassicism", "French", "romantic-neoclassical", 4),
    ("Pierre-Paul Prud'hon", "pierre paul prudhon|prudhon", 1758, 1823, 18, "Neoclassicism", "French", "romantic-neoclassical", 4),
    # --- Japanese prints
    ("Katsushika Hokusai", "katsushika hokusai|hokusai", 1760, 1849, 19, "Ukiyo-e", "Japanese", "japanese-prints", 1),
    ("Utagawa Hiroshige", "utagawa hiroshige|hiroshige", 1797, 1858, 19, "Ukiyo-e", "Japanese", "japanese-prints", 2),
    ("Kitagawa Utamaro", "kitagawa utamaro|utamaro", 1753, 1806, 18, "Ukiyo-e", "Japanese", "japanese-prints", 2),
    ("Utagawa Kuniyoshi", "utagawa kuniyoshi|kuniyoshi", 1798, 1861, 19, "Ukiyo-e", "Japanese", "japanese-prints", 3),
    ("Suzuki Harunobu", "suzuki harunobu|harunobu", 1725, 1770, 18, "Ukiyo-e", "Japanese", "japanese-prints", 4),
    ("Tsukioka Yoshitoshi", "tsukioka yoshitoshi|yoshitoshi", 1839, 1892, 19, "Ukiyo-e", "Japanese", "japanese-prints", 4),
    ("Tōshūsai Sharaku", "toshusai sharaku|sharaku", None, None, 18, "Ukiyo-e", "Japanese", "japanese-prints", 4),
    # --- Vienna & early modern
    ("Gustav Klimt", "gustav klimt|klimt", 1862, 1918, 19, "Symbolism", "Austrian", "vienna-modern", 1),
    ("Egon Schiele", "egon schiele|schiele", 1890, 1918, 20, "Expressionism", "Austrian", "vienna-modern", 2),
    ("Koloman Moser", "koloman moser|moser", 1868, 1918, 19, "Symbolism", "Austrian", "vienna-modern", 4),
    ("Wassily Kandinsky", "wassily kandinsky|vasily kandinsky|kandinsky", 1866, 1944, 20, "Early Modernism", "Russian", "early-modern", 2),
    ("Piet Mondrian", "piet mondrian|mondrian", 1872, 1944, 20, "Early Modernism", "Dutch", "early-modern", 2),
    ("Paul Klee", "paul klee|klee", 1879, 1940, 20, "Early Modernism", "Swiss", "early-modern", 2),
    ("James Ensor", "james ensor|ensor", 1860, 1949, 19, "Symbolism", "Belgian", "early-modern", 3),
    ("Ernst Ludwig Kirchner", "ernst ludwig kirchner|kirchner", 1880, 1938, 20, "Expressionism", "German", "early-modern", 3),
    ("Franz Marc", "franz marc", 1880, 1916, 20, "Expressionism", "German", "early-modern", 3),
    ("Emil Nolde", "emil nolde|nolde", 1867, 1956, 20, "Expressionism", "German", "early-modern", 3),
    ("August Macke", "august macke|macke", 1887, 1914, 20, "Expressionism", "German", "early-modern", 4),
    ("Alexej von Jawlensky", "alexej von jawlensky|jawlensky", 1864, 1941, 20, "Expressionism", "Russian", "early-modern", 4),
    # --- Chinese literati painting
    ("Shen Zhou", "shen zhou", 1427, 1509, 15, "Chinese Literati Painting", "Chinese", "chinese-literati", 3),
    ("Wen Zhengming", "wen zhengming", 1470, 1559, 16, "Chinese Literati Painting", "Chinese", "chinese-literati", 3),
    ("Qiu Ying", "qiu ying", 1494, 1552, 16, "Chinese Literati Painting", "Chinese", "chinese-literati", 4),
    ("Dong Qichang", "dong qichang", 1555, 1636, 16, "Chinese Literati Painting", "Chinese", "chinese-literati", 4),
]

CIRCLES = {
    "impressionists": "the Impressionist circle",
    "post-impressionists": "the Post-Impressionist circle",
    "dutch-golden": "the Dutch Golden Age",
    "flemish-baroque": "the Flemish Baroque",
    "italian-renaissance": "the Italian Renaissance",
    "northern-renaissance": "the Northern Renaissance",
    "roman-baroque": "the Roman Baroque",
    "spanish-masters": "the Spanish masters",
    "barbizon-realists": "the Barbizon school and the Realists",
    "british-classics": "the British school",
    "pre-raphaelites": "the Pre-Raphaelites and Victorians",
    "american-19th": "the American nineteenth century",
    "french-academic": "the French academic and symbolist salons",
    "french-rococo": "the French Rococo",
    "venetian-18th": "the Venetian eighteenth century",
    "romantic-neoclassical": "the Neoclassicists and Romantics",
    "japanese-prints": "the ukiyo-e masters",
    "vienna-modern": "Vienna around 1900",
    "early-modern": "the early modernists",
    "chinese-literati": "the Chinese literati painters",
}

# Canonical works pinned to a level: (artist, title substring, level,
# optional museum id, optional excluded substring). Museum attribution still
# comes from the museum record itself; this list only sets the level of a
# work the museum attributes to that artist under that title.
ICONIC = [
    ("Georges Seurat", "sunday on la grande jatte", 1, "aic", "study"),
    ("Claude Monet", "bridge over a pond of water lilies", 1, "met", None),
    ("Vincent van Gogh", "self portrait with a straw hat", 1, "met", None),
    ("Katsushika Hokusai", "under the wave off kanagawa", 1, None, None),
    ("Katsushika Hokusai", "the great wave", 1, None, None),
    ("Paul Cézanne", "the card players", 1, "met", None),
    ("Frederic Edwin Church", "the heart of the andes", 1, "met", None),
    ("Gustave Caillebotte", "paris street rainy day", 1, "aic", None),
    ("El Greco", "view of toledo", 1, "met", None),
    ("Johannes Vermeer", "young woman with a water pitcher", 2, "met", None),
    ("Rembrandt van Rijn", "self portrait", 2, None, None),
    ("Diego Velázquez", "juan de pareja", 2, "met", None),
    ("John Singer Sargent", "madame x", 2, "met", None),
    ("Thomas Cole", "oxbow", 2, "met", None),
    ("Albert Bierstadt", "rocky mountains", 2, "met", None),
    ("Winslow Homer", "the herring net", 2, "aic", None),
    ("Winslow Homer", "the gulf stream", 2, "met", None),
    ("Mary Cassatt", "the child s bath", 2, "aic", None),
    ("Vincent van Gogh", "the bedroom", 1, "aic", None),
    ("Claude Monet", "water lilies", 1, None, None),
    ("Vincent van Gogh", "self portrait", 2, "aic", None),
    ("Claude Monet", "arrival of the normandy train", 2, "aic", None),
    ("Claude Monet", "stacks of wheat", 2, "aic", None),
    ("Katsushika Hokusai", "fine wind clear morning", 2, None, None),
    ("Katsushika Hokusai", "south wind clear sky", 2, None, None),
    ("Utagawa Hiroshige", "sudden shower over shin ohashi", 2, None, None),
    ("Winslow Homer", "prisoners from the front", 2, "met", None),
    ("Camille Pissarro", "boulevard montmartre", 2, "met", None),
    ("Caspar David Friedrich", "two men contemplating the moon", 2, "met", None),
    ("John Constable", "salisbury cathedral", 3, None, None),
    ("Édouard Manet", "young lady in 1866", 3, "met", None),
    ("Rembrandt van Rijn", "the three crosses", 3, None, None),
    ("Johannes Vermeer", "allegory of faith", 3, "met", None),
    ("Raphael", "the agony in the garden", 3, "met", None),
    ("Eugène Delacroix", "the natchez", 3, "met", None),
    ("Edgar Degas", "the dance class", 2, "met", None),
    ("Francisco Goya", "the sleep of reason", 2, None, None),
    ("Francisco Goya", "sueno de la razon", 2, None, None),
    ("Albrecht Dürer", "melencolia", 2, None, None),
    ("Albrecht Dürer", "four horsemen", 2, None, None),
    ("Jacques-Louis David", "the death of socrates", 2, "met", None),
    ("Édouard Manet", "boating", 2, "met", None),
    ("Pierre-Auguste Renoir", "two sisters", 2, "aic", None),
    ("Paul Gauguin", "ia orana maria", 2, "met", None),
    ("Henri de Toulouse-Lautrec", "at the moulin rouge", 2, "aic", None),
    ("Caravaggio", "crucifixion of saint andrew", 2, "cle", None),
    ("J.M.W. Turner", "the grand canal", 2, "met", None),
    ("Frans Hals", "merrymakers at shrovetide", 3, "met", None),
    ("Titian", "venus and the lute player", 3, "met", None),
    ("Sandro Botticelli", "last communion of saint jerome", 3, "met", None),
    ("Artemisia Gentileschi", "esther before ahasuerus", 3, "met", None),
    ("Antoine Watteau", "mezzetin", 3, "met", None),
    ("Gustave Courbet", "woman in the waves", 3, "met", None),
    ("Thomas Eakins", "max schmitt in a single scull", 3, "met", None),
    ("Gustav Klimt", "primavesi", 3, "met", None),
    ("Utagawa Hiroshige", "plum park at kameido", 3, None, None),
    ("Peter Paul Rubens", "wolf and fox hunt", 3, "met", None),
]

# Artist strings carrying these qualifiers are not firm attributions.
QUALIFIERS = ("after ", "attributed to", "follower", "circle of", "workshop",
              "manner of", "copy after", "imitator", "school of", "studio of",
              "formerly attributed", "pseudo", "unknown", "unidentified",
              "anonymous")
# Per-artist extra exclusions (normalised substrings in the museum string).
EXCLUDE = {"Rembrandt van Rijn": ("peale",), "George Inness": ("jr",)}


# ---------------------------------------------------------------- helpers
def norm(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace('&', ' and ')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def tokens(s):
    return set(norm(s).split())


ARTISTS = []
for (name, aliases, b, d, c, mov, nat, cir, tier) in ROSTER:
    ARTISTS.append({
        'name': name, 'aliases': [norm(a) for a in aliases.split('|')],
        'birth': b, 'death': d, 'century': c, 'movement': mov,
        'nationality': nat, 'circle': cir, 'tier': tier,
    })
BY_NAME = {a['name']: a for a in ARTISTS}


NAME_SUFFIXES = {'the', 'younger', 'elder', 'i', 'ii', 'iii', 'jr', 'sr', 'senior', 'junior'}


def match_artist(museum_artist):
    """Return the roster artist a museum artist string firmly names, else None.
    Multi-token aliases match as token subsets, longest alias wins (so
    'Théodore Rousseau' is not captured by Henri Rousseau's surname).
    A single-token alias (bare surname / mononym) matches ONLY when the
    record carries no other personal name — otherwise 'David Lucas' (the
    engraver) would match Jacques-Louis David, 'Jan Peeters' would match
    Clara Peeters, and 'Rosa Bonheur' would match Salvator Rosa."""
    raw = norm(museum_artist)
    if not raw or any(q in raw for q in QUALIFIERS):
        return None
    mt = set(raw.split())
    best, best_len = None, 0
    for a in ARTISTS:
        if any(x in raw for x in EXCLUDE.get(a['name'], ())):
            continue
        for al in a['aliases']:
            at = set(al.split())
            if not at or not at <= mt:
                continue
            if len(at) >= 2:
                if len(at) > best_len:
                    best, best_len = a, len(at)
            elif not (mt - at - NAME_SUFFIXES):
                if best is None:
                    best, best_len = a, 1
    return best


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


# ---------------------------------------------------------------- the Met
MET = 'The Metropolitan Museum of Art'
MET_CLASSES = {'Paintings', 'Prints', 'Drawings'}


def met_candidates(a):
    q = urllib.parse.quote(a['name'])
    ids = []
    for offset in (0, 100):
        url = (f'https://collectionapi.metmuseum.org/public/collection/v1.1/search'
               f'?q={q}&hasImages=true&artistOrCulture=true&limit=100&offset={offset}')
        try:
            d = get_json(url)
        except Exception:
            break
        ids += d.get('objectIDs') or []
        if len(ids) >= (d.get('total') or 0) or not d.get('objectIDs'):
            break
    ids = list(dict.fromkeys(ids))[:120]

    out = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        for rec in ex.map(lambda oid: met_object(a, oid), ids):
            if rec:
                out.append(rec)
                if len(out) >= 30:
                    break
    return out


def met_object(a, oid):
    try:
        o = get_json(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}')
    except Exception:
        return None
    if not o.get('isPublicDomain') or not o.get('primaryImage'):
        return None
    # Some genuine paintings carry an empty classification in the Met's
    # data (Heart of the Andes, Madame X, the Oxbow); accept those, but
    # not the filled non-picture classifications.
    if o.get('classification') not in MET_CLASSES and o.get('classification'):
        return None
    if match_artist(o.get('artistDisplayName') or '') is not a:
        return None
    title = (o.get('title') or '').strip()
    if len(title) < 3:
        return None
    return {'artist': a['name'], 'title': title,
            'date': (o.get('objectDate') or '').strip(),
            'museum': MET, 'museumId': 'met',
            'objectUrl': o.get('objectURL') or '',
            'image': o.get('primaryImageSmall') or o.get('primaryImage'),
            'highlight': bool(o.get('isHighlight')),
            '_class': o.get('classification') or ''}


# ---------------------------------------------------------------- Cleveland
CLE = 'The Cleveland Museum of Art'
CLE_TYPES = {'Painting', 'Print', 'Drawing'}


def cle_candidates(a):
    q = urllib.parse.quote(a['name'])
    url = (f'https://openaccess-api.clevelandart.org/api/artworks/'
           f'?q={q}&cc0=1&has_image=1&limit=100'
           f'&fields=id,title,creators,creation_date,url,images,type')
    try:
        d = get_json(url)
    except Exception:
        return []
    out = []
    for o in d.get('data') or []:
        if o.get('type') not in CLE_TYPES:
            continue
        img = ((o.get('images') or {}).get('web') or {}).get('url')
        if not img:
            continue
        hit = None
        for cr in o.get('creators') or []:
            desc = (cr.get('description') or '').split('(')[0].strip()
            if match_artist(desc) is a:
                hit = a
                break
        if not hit:
            continue
        title = (o.get('title') or '').strip()
        if len(title) < 3:
            continue
        out.append({'artist': a['name'], 'title': title,
                    'date': (o.get('creation_date') or '').strip(),
                    'museum': CLE, 'museumId': 'cle',
                    'objectUrl': o.get('url') or '', 'image': img,
                    'highlight': False})
    return out


# ---------------------------------------------------------------- AIC (dump)
AIC = 'Art Institute of Chicago'
AIC_TYPES = {'Painting', 'Print', 'Drawing and Watercolor'}


def aic_candidates():
    """Stream the museum's data dump once; bucket PD works by roster artist."""
    buckets = {a['name']: [] for a in ARTISTS}
    surnames = {}
    for a in ARTISTS:
        for al in a['aliases']:
            surnames.setdefault(al.split()[-1], []).append(a)
    with tarfile.open(AIC_TARBALL, 'r|bz2') as tf:
        for m in tf:
            if not m.isfile() or '/artworks/' not in m.name or not m.name.endswith('.json'):
                continue
            f = tf.extractfile(m)
            if f is None:
                continue
            try:
                o = json.loads(f.read().decode('utf-8'))
            except Exception:
                continue
            if not o.get('is_public_domain') or not o.get('image_id'):
                continue
            if o.get('artwork_type_title') not in AIC_TYPES:
                continue
            at = o.get('artist_title') or ''
            a = match_artist(at)
            if a is None:
                continue
            title = (o.get('title') or '').strip()
            if len(title) < 3:
                continue
            buckets[a['name']].append({
                'artist': a['name'], 'title': title,
                'date': (o.get('date_display') or '').strip(),
                'museum': AIC, 'museumId': 'aic',
                'objectUrl': f"https://www.artic.edu/artworks/{o['id']}",
                'image': f"https://www.artic.edu/iiif/2/{o['image_id']}/full/843,/0/default.jpg",
                'highlight': False})
    return buckets


# ---------------------------------------------------------------- mediums
# Every pooled work also carries the holding museum's own medium string
# and a coarse "kind" derived from the museum's classification of that
# exact object, so the game can ask the right question — "Who drew
# this?" for a drawing, "Who made this print?" for a print — instead of
# calling everything a painting. Mediums are fetched per object from
# the museum record itself (Met: classification + medium; AIC:
# artwork_type_title + medium_display, from the data dump; Cleveland:
# type + technique) and cached in MEDIUM_CACHE so rebuilds are cheap.
# A work whose record cannot be retrieved keeps an empty medium and
# kind "other"; kinds are never guessed from titles.
MEDIUM_CACHE = '/tmp/game-pool-mediums.json'

KIND_BY_MET_CLASS = {'Paintings': 'painting', 'Drawings': 'drawing',
                     'Prints': 'print'}
KIND_BY_AIC_TYPE = {'Painting': 'painting', 'Print': 'print',
                    'Drawing and Watercolor': 'drawing',
                    'Photograph': 'photograph', 'Sculpture': 'sculpture'}
KIND_BY_CLE_TYPE = {'Painting': 'painting', 'Print': 'print',
                    'Drawing': 'drawing', 'Photograph': 'photograph',
                    'Sculpture': 'sculpture'}

# Fallback wording tests on a museum medium string, used only when the
# record's own classification is missing (the Met leaves the
# classification empty on some genuine paintings — the Heart of the
# Andes among them). Print techniques are tested first: a woodblock
# print's medium also mentions ink.
_PRINT_TERMS = ('woodblock', 'engraving', 'etching', 'woodcut', 'lithograph',
                'drypoint', 'aquatint', 'mezzotint', 'linocut', 'screenprint',
                'serigraph', 'photogravure', 'print')
_PHOTO_TERMS = ('photograph', 'gelatin silver', 'albumen', 'daguerreotype',
                'chromogenic', 'platinum print', 'cyanotype')
_PAINT_TERMS = ('oil on', 'oil and', 'tempera', 'acrylic', 'encaustic',
                'fresco', 'casein')
_DRAW_TERMS = ('watercolor', 'watercolour', 'gouache', 'graphite', 'pencil',
               'chalk', 'charcoal', 'pastel', 'crayon', 'pen and', 'ink',
               'wash', 'drawing')


def kind_from_medium(medium):
    m = norm(medium)
    if not m:
        return 'other'
    if any(t in m for t in _PRINT_TERMS):
        return 'print'
    if any(t in m for t in _PHOTO_TERMS):
        return 'photograph'
    if any(t in m for t in _PAINT_TERMS):
        return 'painting'
    if any(t in m for t in _DRAW_TERMS):
        return 'drawing'
    return 'other'


def _met_medium(url):
    m = re.search(r'(\d+)/?$', url or '')
    if not m:
        return None
    o = get_json('https://collectionapi.metmuseum.org/public/collection/v1'
                 f'/objects/{m.group(1)}')
    medium = (o.get('medium') or '').strip()
    kind = KIND_BY_MET_CLASS.get(o.get('classification') or '') \
        or kind_from_medium(medium)
    return {'medium': medium, 'kind': kind}


def _cle_medium(url):
    m = re.search(r'/art/(.+)$', url or '')
    if not m:
        return None
    acc = urllib.parse.quote(m.group(1), safe='')
    d = get_json('https://openaccess-api.clevelandart.org/api/artworks/'
                 f'?accession_number={acc}')
    rows = d.get('data') or []
    if not rows:
        return None
    o = rows[0]
    medium = (o.get('technique') or '').strip()
    kind = KIND_BY_CLE_TYPE.get(o.get('type') or '') \
        or kind_from_medium(medium)
    return {'medium': medium, 'kind': kind}


def _aic_mediums(urls):
    """One streaming pass over the museum's data dump, picking out the
    records for the given object URLs (the live AIC API is bot-walled
    from the build network; see aic_candidates)."""
    ids = {}
    for u in urls:
        m = re.search(r'/artworks/(\d+)', u or '')
        if m:
            ids[int(m.group(1))] = u
    out = {}
    if not ids:
        return out
    with tarfile.open(AIC_TARBALL, 'r|bz2') as tf:
        for m in tf:
            if not m.isfile() or '/artworks/' not in m.name \
                    or not m.name.endswith('.json'):
                continue
            try:
                aid = int(m.name.rsplit('/', 1)[-1][:-5])
            except ValueError:
                continue
            if aid not in ids:
                continue
            f = tf.extractfile(m)
            if f is None:
                continue
            try:
                o = json.loads(f.read().decode('utf-8'))
            except Exception:
                continue
            medium = (o.get('medium_display') or '').strip()
            kind = KIND_BY_AIC_TYPE.get(o.get('artwork_type_title') or '') \
                or kind_from_medium(medium)
            out[ids[aid]] = {'medium': medium, 'kind': kind}
            if len(out) == len(ids):
                break
    return out


def augment_mediums(works):
    """Attach medium + kind to each work, from its museum record.
    Returns the number of works whose record could not be retrieved
    (they keep an empty medium and kind "other")."""
    import os
    cache = {}
    if os.path.exists(MEDIUM_CACHE):
        try:
            cache = json.load(open(MEDIUM_CACHE))
        except Exception:
            cache = {}
    todo = [w for w in works if w.get('objectUrl') not in cache]
    if todo:
        fetched = {}

        def fetch_one(w):
            try:
                rec = _met_medium(w['objectUrl']) if w['museum'] == MET \
                    else _cle_medium(w['objectUrl'])
                return w['objectUrl'], rec
            except Exception:
                return w['objectUrl'], None

        singles = [w for w in todo if w['museum'] in (MET, CLE)]
        with ThreadPoolExecutor(max_workers=10) as ex:
            for url, rec in ex.map(fetch_one, singles):
                if rec:
                    fetched[url] = rec
        try:
            fetched.update(_aic_mediums(
                [w['objectUrl'] for w in todo if w['museum'] == AIC]))
        except Exception as e:
            print(f'  AIC mediums unavailable: {e}', flush=True)
        cache.update(fetched)
        with open(MEDIUM_CACHE, 'w') as f:
            json.dump(cache, f)
        print(f'Mediums: fetched {len(fetched)} of {len(todo)} outstanding',
              flush=True)
    missing = 0
    for w in works:
        rec = cache.get(w.get('objectUrl'))
        if rec:
            w['medium'], w['kind'] = rec['medium'], rec['kind']
        else:
            w['medium'], w['kind'] = '', 'other'
            missing += 1
    return missing


# ---------------------------------------------------------------- levels
def title_matches(nt, ns):
    """Pattern-in-title test; a leading 'the' in the pattern is optional,
    since museums differ on including the article (the Met's Church is
    'Heart of the Andes', not 'The Heart of the Andes')."""
    if ns in nt:
        return True
    return ns.startswith('the ') and ns[4:] in nt


def iconic_level(rec):
    nt = norm(rec['title'])
    for (artist, sub, lvl, mus, excl) in ICONIC:
        if rec['artist'] != artist:
            continue
        if mus and rec['museumId'] != mus:
            continue
        if excl and excl in nt:
            continue
        if title_matches(nt, norm(sub)):
            return lvl
    return None


BANDS = {1: (3, 4, 4, 5), 2: (4, 5, 5, 6), 3: (6, 7, 7, 8), 4: (8, 9, 9, 10)}


def band_level(rec):
    a = BY_NAME[rec['artist']]
    band = BANDS[a['tier']]
    h = int(hashlib.md5(norm(rec['title']).encode()).hexdigest(), 16)
    lvl = band[h % len(band)]
    if rec.get('highlight'):
        lvl = max(band[0], lvl - 1)
    return lvl


def iconic_match(rec, artist, sub, mus, excl):
    if rec['artist'] != artist:
        return False
    if mus and rec.get('museumId') != mus:
        return False
    nt = norm(rec['title'])
    if excl and excl in nt:
        return False
    return title_matches(nt, norm(sub))


def rescue_iconics(cand):
    """Iconic works the per-artist harvest can miss (the Met search cap
    cuts lower-ranked results): fetch them by a title search instead.
    Attribution still comes from the museum record itself."""
    added = []
    have = [(r['artist'], norm(r['title']), r.get('museumId')) for r in cand]

    def already(artist, sub, mus, excl):
        ns = norm(sub)
        return any(ar == artist and (not mus or mid == mus)
                   and (not excl or excl not in nt) and title_matches(nt, ns)
                   for (ar, nt, mid) in have)
    for (artist, sub, lvl, mus, excl) in ICONIC:
        if already(artist, sub, mus, excl):
            continue
        a = BY_NAME[artist]
        words = ' '.join(sub.split()[:5])
        if mus in (None, 'met'):
            q = urllib.parse.quote(words)
            url = (f'https://collectionapi.metmuseum.org/public/collection/v1.1/search'
                   f'?q={q}&title=true&hasImages=true&limit=120')
            try:
                d = get_json(url)
            except Exception:
                d = {}
            ids = (d.get('objectIDs') or [])[:120]
            hits = []
            with ThreadPoolExecutor(max_workers=10) as ex:
                for rec in ex.map(lambda oid: met_object(a, oid), ids):
                    if rec and iconic_match(rec, artist, sub, mus, excl):
                        hits.append(rec)
            if hits:
                # Prefer the painting over drawings/prints of the same title.
                hits.sort(key=lambda r: {'Paintings': 0, 'Drawings': 1, 'Prints': 2}.get(r.get('_class'), 1))
                rec = hits[0]
                added.append(rec)
                have.append((rec['artist'], norm(rec['title']), rec.get('museumId')))
        if already(artist, sub, mus, excl):
            continue
        if mus in (None, 'cle'):
            q = urllib.parse.quote(words)
            url = (f'https://openaccess-api.clevelandart.org/api/artworks/'
                   f'?q={q}&cc0=1&has_image=1&limit=20'
                   f'&fields=id,title,creators,creation_date,url,images,type')
            try:
                d = get_json(url)
            except Exception:
                d = {}
            for o in d.get('data') or []:
                if o.get('type') not in CLE_TYPES:
                    continue
                img = ((o.get('images') or {}).get('web') or {}).get('url')
                if not img:
                    continue
                if not any(match_artist((cr.get('description') or '').split('(')[0].strip()) is a
                           for cr in o.get('creators') or []):
                    continue
                rec = {'artist': a['name'], 'title': (o.get('title') or '').strip(),
                       'date': (o.get('creation_date') or '').strip(),
                       'museum': CLE, 'museumId': 'cle',
                       'objectUrl': o.get('url') or '', 'image': img, 'highlight': False}
                if len(rec['title']) >= 3 and iconic_match(rec, artist, sub, mus, excl):
                    added.append(rec)
                    have.append((rec['artist'], norm(rec['title']), rec.get('museumId')))
                    break
    if added:
        print(f'Rescued {len(added)} iconic works by title search', flush=True)
    return added


CACHE = '/tmp/game-pool-candidates.json'


def harvest():
    print('Harvesting the Met and Cleveland…', flush=True)
    cand = []
    for i, a in enumerate(ARTISTS):
        got = []
        try:
            got += met_candidates(a)
        except Exception as e:
            print(f"  Met failed for {a['name']}: {e}", flush=True)
        try:
            got += cle_candidates(a)
        except Exception as e:
            print(f"  Cleveland failed for {a['name']}: {e}", flush=True)
        cand += got
        if (i + 1) % 25 == 0:
            print(f'  {i + 1}/{len(ARTISTS)} artists, {len(cand)} candidates', flush=True)
    print('Streaming the AIC dump…', flush=True)
    buckets = aic_candidates()
    n_aic = sum(len(v) for v in buckets.values())
    for v in buckets.values():
        cand += v
    print(f'Candidates: {len(cand)} (AIC contributed {n_aic})', flush=True)
    return cand


def title_sim(a, b):
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def dedupe(cand):
    """Drop near-duplicate titles per artist (the same work or impression
    catalogued under slightly different titles at different museums).
    Museum priority Met > AIC > Cleveland, then the shorter title."""
    prio = {'met': 0, 'aic': 1, 'cle': 2}
    cand = sorted(cand, key=lambda r: (prio[r['museumId']], len(norm(r['title']))))
    kept, seen = [], {}
    for rec in cand:
        nt = norm(rec['title'])
        lst = seen.setdefault(rec['artist'], [])
        if any(title_sim(nt, t) >= 0.6 for t in lst):
            continue
        lst.append(nt)
        kept.append(rec)
    return kept


def main():
    import os
    if '--augment-only' in sys.argv:
        # Refresh just the medium/kind fields of the shipped pool from
        # the museum records; works, levels and order stay untouched.
        doc = json.load(open(OUT))
        missing = augment_mediums(doc['works'])
        with open(OUT, 'w') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        from collections import Counter
        print('Kinds:', dict(Counter(w['kind'] for w in doc['works'])))
        print(f'Augmented {OUT}: {len(doc["works"])} works, '
              f'{missing} without a retrievable museum medium')
        return
    if '--fresh' not in sys.argv and os.path.exists(CACHE):
        cand = json.load(open(CACHE))
        print(f'Loaded {len(cand)} candidates from cache (use --fresh to re-harvest)', flush=True)
    else:
        cand = harvest()
        with open(CACHE, 'w') as f:
            json.dump(cand, f)
    rescued = rescue_iconics(cand)
    if rescued:
        cand += rescued
        with open(CACHE, 'w') as f:
            json.dump(cand, f)
    cand = dedupe(cand)
    print(f'After dedupe: {len(cand)}', flush=True)

    # Per-artist selection: iconic first, then highlights, then the rest;
    # cap 6 per artist so no single name floods the pool.
    for rec in cand:
        rec['_iconic'] = iconic_level(rec)
    # Drop records whose "title" is only a date range (portfolio covers
    # and the like) — they read as broken in the verdict panel.
    cand = [r for r in cand if not re.fullmatch(r'\d{4}( \d{4})?', norm(r['title']))]
    by_artist = {}
    for rec in cand:
        by_artist.setdefault(rec['artist'], []).append(rec)
    pool = []
    for name, recs in by_artist.items():
        recs.sort(key=lambda r: (r['_iconic'] is None, not r['highlight'], norm(r['title'])))
        pool += recs[:6]
    print(f'After per-artist cap: {len(pool)}', flush=True)

    # Levels: iconic pins first, banding for the rest.
    for rec in pool:
        rec['level'] = rec['_iconic'] if rec['_iconic'] else band_level(rec)

    # Rebalance: every level >= 15 works (move non-iconic works from the
    # fullest neighbouring level), no level > 34 (spill non-iconic works
    # to the emptiest neighbour).
    def counts():
        c = {i: 0 for i in range(1, 11)}
        for r in pool:
            c[r['level']] += 1
        return c
    for _ in range(60):
        c = counts()
        # Levels 1-3 are never filled by moving banded works: they hold
        # canonical works only (iconic pins, plus tier-1 band works at 3).
        lacking = [l for l in range(4, 11) if c[l] < 15]
        if not lacking:
            break
        tgt = lacking[0]
        donors = sorted((l for l in range(3, 11) if abs(l - tgt) == 1 and c[l] > 20),
                        key=lambda l: -c[l])
        if not donors:
            break
        src = donors[0]
        movable = [r for r in pool if r['level'] == src and r['_iconic'] is None]
        if not movable:
            break
        movable.sort(key=lambda r: norm(r['title']))
        movable[0]['level'] = tgt
    # Over-full levels are NOT spilled into neighbouring levels (that
    # would drag arbitrary works into the canonical low levels); the
    # trim after the image check caps each level at 30 instead.
    print('Levels before image check:', counts(), flush=True)

    # Verify every image actually loads; drop failures. AIC is the one
    # exception: artic.edu's CDN bot-walls direct requests from the build
    # server (its API is walled the same way), while the same IIIF URLs
    # serve normally to browsers — so AIC images pass here and are
    # verified afterwards through an independent fetch path (see POOL.md).
    def ok(rec):
        if rec['museumId'] == 'aic':
            return True
        for method in ('HEAD', 'GET'):
            try:
                req = urllib.request.Request(rec['image'], headers=UA, method=method)
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status == 200:
                        return True
            except Exception:
                continue
        return False
    good = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        flags = list(ex.map(ok, pool))
    for rec, flag in zip(pool, flags):
        if flag:
            good.append(rec)
        else:
            print(f"  image failed, dropped: {rec['artist']} — {rec['title']}", flush=True)
    pool = good
    print('Levels after image check:', counts(), flush=True)

    # Trim to a balanced few hundred: at most 30 works per level, at most
    # 3 per artist per level; canonical (iconic) works and museum
    # highlights are kept first, the rest spread deterministically.
    by_level = {}
    for r in pool:
        by_level.setdefault(r['level'], []).append(r)
    trimmed = []
    for lvl, recs in sorted(by_level.items()):
        cap = 40 if lvl <= 3 else 30  # the canonical levels keep more depth
        if len(recs) <= cap:
            trimmed += recs
            continue
        recs.sort(key=lambda r: (r['_iconic'] is None, not r['highlight'],
                                 hashlib.md5((r['artist'] + '|' + norm(r['title'])).encode()).hexdigest()))
        chosen, per_artist, chosen_ids = [], {}, set()
        for r in recs:
            if len(chosen) >= cap:
                break
            if per_artist.get(r['artist'], 0) >= 3:
                continue
            per_artist[r['artist']] = per_artist.get(r['artist'], 0) + 1
            chosen.append(r)
            chosen_ids.add(id(r))
        if len(chosen) < cap:
            chosen += [r for r in recs if id(r) not in chosen_ids][:cap - len(chosen)]
        trimmed += chosen
    pool = trimmed
    print('Levels after trim:', counts(), flush=True)

    pool.sort(key=lambda r: (r['level'], r['artist'], norm(r['title'])))
    works = [{'artist': r['artist'], 'title': r['title'], 'date': r['date'],
              'museum': r['museum'], 'objectUrl': r['objectUrl'],
              'image': r['image'], 'level': r['level']} for r in pool]
    missing = augment_mediums(works)
    if missing:
        print(f'WARNING: {missing} works have no retrievable museum '
              f'medium; kind set to "other"', flush=True)
    artists = {a['name']: {'birth': a['birth'], 'death': a['death'],
                           'century': a['century'], 'movement': a['movement'],
                           'nationality': a['nationality'], 'circle': a['circle'],
                           'tier': a['tier']} for a in ARTISTS}
    doc = {'generated': time.strftime('%Y-%m-%d'),
           'about': ('Open-access works only. Every work is the museum\'s own '
                     'record for that object; the artist shown is the artist '
                     'that record names.'),
           'circles': CIRCLES, 'artists': artists, 'works': works}
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f'Wrote {OUT}: {len(works)} works')
    c = counts()
    for l in range(1, 11):
        print(f'  level {l}: {c[l]}')


if __name__ == '__main__':
    main()

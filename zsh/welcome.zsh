# Simple red-themed zsh welcome message

# Red color
RED='\033[0;31m'
NC='\033[0m' # No Color

# Simple welcome function
simple_welcome() {
    echo ""
    echo "${RED}⠀⠀⠀⠀⡀⡀⡀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⠀⠀⢀⢎⢎⣜⡼⣱⣧⠤⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⠀⡠⢣⡿⡯⣪⣾⣿⢿⣳⣎⠻⣦⣍⡲⡤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⣎⣆⣯⢰⣾⠫⢹⢷⡟⠉⠉⣛⠉⠉⣻⠿⢤⣑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⡸⠻⣣⣿⣿⣿⣵⣿⣟⢝⣿⣿⣿⣿⣷⣤⣴⣾⠿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⠓⠚⢹⣿⢾⢿⣻⣽⡇⢰⣿⣿⣿⣿⣿⣿⣿⣄⣰⣺⣧⠀⢔⢦⡲⣔⢦⡲⣄⠀⠀⠀${NC}"
    echo "${RED}⠀⠀⡠⣿⣯⣭⣴⣿⡇⢸⣿⠉⠑⠑⠝⠝⣽⠟⡟⠉⠙⡄⢸⢸⡇⣿⢸⡇⣿⣧⠀⠀${NC}"
    echo "${RED}⠀⡸⠚⢿⣿⣿⣿⣿⡷⠃⠐⡇⠀⠀⢀⠜⠀⢀⣻⣶⣾⡟⠘⢸⢇⡿⣸⢇⣿⣿⠀⠀${NC}"
    echo "${RED}⡜⣀⠤⣾⣿⣿⣿⣿⠃⠀⢴⡇⠀⡔⠁⣱⣄⣞⣾⣿⣿⡷⠾⠿⣾⣷⣿⣏⣹⣿⠀⠀${NC}"
    echo "${RED}⡜⢠⠊⡸⢻⣟⠝⠁⠀⠀⡴⠀⠸⢔⠞⠉⡸⠿⣿⣿⣿⣇⣀⢤⣶⣿⣿⠋⣸⣀⡠⠔${NC}"
    echo "${RED}⠑⢇⠜⡀⡎⠀⠀⡠⠒⢻⠀⠀⠪⠥⢔⣈⣤⡪⠝⢻⣿⣿⣿⣾⣿⣿⡿⢲⠛⠛⢀⠀${NC}"
    echo "${RED}⠀⠀⠀⠈⠀⠀⢰⣅⣀⣼⣤⣤⣀⣀⣀⣠⣤⣴⣾⣿⠉⠀⠈⣿⣿⣟⡠⠿⠶⠊⠁⠀${NC}"
    echo "${RED}⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⣮⣮⣾⣿⣿⣿⣿⣷⣶⣾⣿⣿⣿⣧⣤⠒⠁⠀⠀${NC}"
    echo "${RED}⠀⠀⠀⠀⠀⠀⣀⢼⢿⡿⢿⢟⣿⣿⠉⠉⠛⠛⠛⠛⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀${NC}"
    echo "${RED}⠀⠀⠀⠀⠀⠪⣔⡡⣌⣀⠤⠝⠋⠁⠀⠀⠀⠀⠀⡰⢋⡛⠙⣿⠋⢻⠇⠀⠀⠀⠀⠀${NC}"
    echo "${RED}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠑⠜⠀⠢⠃⠀⠀⠀⠀⠀⠀${NC}"
    echo ""
    echo "    User: $(whoami)"
    echo "    Location: $(pwd | sed "s|$HOME|~|")"
    echo "    Time: $(date '+%I:%M %p')"
    echo ""
}

simple_welcome

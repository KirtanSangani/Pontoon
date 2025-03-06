# Blackjack
# From 1 to 7 players compete against a dealer

import cards, games     

class P_Card(cards.Card):
    """ A Pontoon Card. """
    ACE_VALUE = 1

    @property
    def value(self):
        if self.is_face_up:
            v = P_Card.RANKS.index(self.rank) + 1
            if v > 10:
                v = 10
        else:
            v = None
        return v

class P_Deck(cards.Deck):
    """ A Pontoon Deck. """
    def populate(self):
        for suit in P_Card.SUITS: 
            for rank in P_Card.RANKS: 
                self.cards.append(P_Card(rank, suit))
    

class P_Hand(cards.Hand):
    """ A Pontoon Hand. """
    def __init__(self, name):
        super(P_Hand, self).__init__()
        self.name = name

    def __str__(self):
        rep = self.name + ":\t" + super(P_Hand, self).__str__()  
        if self.total:
            rep += "(" + str(self.total) + ")"        
        return rep

    @property     
    def total(self):
        # if a card in the hand has value of None, then total is None
        for card in self.cards:
            if not card.value:
                return None
        
        # add up card values, treat each Ace as 1
        t = 0
        for card in self.cards:
              t += card.value

        # determine if hand contains an Ace
        contains_ace = False
        for card in self.cards:
            if card.value == P_Card.ACE_VALUE:
                contains_ace = True
                
        # if hand contains Ace and total is low enough, treat Ace as 11
        if contains_ace and t <= 11:
            # add only 10 since we've already added 1 for the Ace
            t += 10   
                
        return t

    def five_card(self):
        count = 0
        # if testing for five card scenario
        # count = 4
        
        for cards in self.cards:
            count += 1
            
        win = False
        if count == 5:
            win = True

        
        return self.total < 21 and win
    
    
    def is_busted(self):
        return self.total > 21


class P_Player(P_Hand):
    """ A Pontoon Player. """
    def __init__(self, name, money, betting, cont, done):
        super().__init__(name)
        self.money = money
        self.betting = 0
        self.cont = cont
        self.done = False
        
    def is_hitting(self):
        cont = True
        if self.betting == 0 and self.total < 21:
            response = games.ask_yes_no("\n" + self.name + ", do you want a hit? (Y/N): ")
            if response == "n":
                cont = False
        else:
            cont = False
        return cont
    
    def get_cont(self):
        return self.cont
    
    def bet(self):
        print(self.name + ": You have $" + str(self.money))
        print("You bet $10")

    def double_down(self):
            self.betting = 1

    def surrender(self):
        self.cont = True
        response = input(self.name + ": Do you want to surrender? (Y/N)")
        if response.lower() == "y":
            self.money -= 5
            self.cont = False
        return self.cont
            
    def bust(self):
        print(self.name, "busts.")
        self.lose()

    def lose(self):
        print(self.name, "loses.")
        self.money -= 10

    def win(self):
        print(self.name, "wins.")
        if self.total == 21:
            self.money += (10 * 1.5)
        else:
            self.money += (10 * 2)
        self.done = True
        

        
class P_Dealer(P_Hand):
    """ A Pontoon Dealer. """
    def is_hitting(self):
        return self.total < 17

    def bust(self):
        print(self.name, "busts.")

    def flip_first_card(self):
        first_card = self.cards[0]
        first_card.flip()
        second_card = self.cards[1]
        second_card.flip()    


class P_Game(object):
    """ A Pontoon Game. """
    def __init__(self, names):      
        self.players = []
        for name in names:
            player = P_Player(name, 100.0, 0, True, False)
            self.players.append(player)

        self.dealer = P_Dealer("Dealer")
        self.deck = P_Deck()
        self.deck.populate()
        self.deck.shuffle()

    @property
    def still_playing(self):
        sp = []
        for player in self.players:
            if not player.is_busted() and player.cont == True:
                sp.append(player)
                print(player)
        return sp

    def __player_additional_cards(self, player):
        # if testing for 21
        player.done = False
        player.clear()
        player.add(P_Card("A","c"))
        player.add(P_Card("K","d"))
        """
        if player.surrender() == False:
            print("Player had surrendered")
        else:
            if player.betting == 0:
                response = input("Do you want to double down? (Y/N)")
                if response.lower() == "y":
                    player.money -= 10
                    self.deck.deal([player])
                    player.double_down()
                
                while not player.is_busted() and player.is_hitting() and player.total < 21:
                    self.deck.deal([player])
                    print(player)
                    if player.five_card():
                        player.win()
                    elif player.total == 21:
                        player.win()
                    elif player.is_busted():
                        player.bust()
        """             
        
    def __dealer_additional_cards(self, player):
            while not player.is_busted() and player.is_hitting():
                self.deck.deal([player])
                print(player)
                if player.is_busted():
                    player.bust()
           
    def play(self):
        # deal initial 2 cards to everyone
        self.deck.deal(self.players + [self.dealer], per_hand = 2)
        self.dealer.flip_first_card()    # hide dealer's first card
        for player in self.players:
            player.betting = 0
            player.bet()
            print(player)
        print(self.dealer)
        
        # deal additional cards to players
        for player in self.players:
            self.__player_additional_cards(player)
                

        if player.done == False:
            if not self.still_playing:
                # since all plazyers have busted, just show the dealer's hand
                self.dealer.flip_first_card()
                print(self.dealer)
            else:
                # deal additional cards to dealer
                self.dealer.flip_first_card()    # reveal dealer's first
                print(self.dealer)
                if player.get_cont() == True:
                    self.__dealer_additional_cards(self.dealer)

                    if self.dealer.is_busted():
                        # everyone still playing wins
                        for player in self.still_playing:
                            player.win()
  
                    else:
                        # compare each player still playing to dealer
                        for player in self.still_playing:
                            if player.total > self.dealer.total:
                                player.win()
                            elif player.total <= self.dealer.total:
                                player.lose()

        # remove everyone's cards
        for player in self.players:
            player.clear()
            print(player.name + ": You have $" + str(player.money))
        self.dealer.clear()
        self.deck.populate()
        self.deck.shuffle()

        

def main():
    print("\t\tWelcome to Blackjack!\n")
    
    names = []
    number = games.ask_number("How many players? (1 - 7): ", low = 1, high = 8)
    for i in range(number):
        name = input("Enter player name: ")
        names.append(name)
    print()
        
    game = P_Game(names)

    again = None
    while again != "n":
        game.play()
        again = games.ask_yes_no("\nDo you want to play again?: ")


main()
input("\n\nPress the enter key to exit.")

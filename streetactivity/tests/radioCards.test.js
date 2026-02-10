describe('Radio Cards', () => {
  test('should manage card selection state', () => {
    const createRadioGroup = () => {
      return {
        cards: [
          { id: 1, selected: false, className: '' },
          { id: 2, selected: false, className: '' },
          { id: 3, selected: false, className: '' }
        ],
        selectCard(cardId) {
          // Reset all
          this.cards.forEach(card => {
            card.selected = false;
            card.className = 'border-light';
          });
          
          // Select one
          const card = this.cards.find(c => c.id === cardId);
          if (card) {
            card.selected = true;
            card.className = 'border-primary';
          }
        }
      };
    };
    
    const group = createRadioGroup();
    
    // Initially none selected
    expect(group.cards[0].selected).toBe(false);
    expect(group.cards[1].selected).toBe(false);
    expect(group.cards[2].selected).toBe(false);
    
    // Select first card
    group.selectCard(1);
    expect(group.cards[0].selected).toBe(true);
    expect(group.cards[0].className).toBe('border-primary');
    expect(group.cards[1].selected).toBe(false);
    expect(group.cards[1].className).toBe('border-light');
    expect(group.cards[2].selected).toBe(false);
    expect(group.cards[2].className).toBe('border-light');
    
    // Select different card
    group.selectCard(3);
    expect(group.cards[0].selected).toBe(false);
    expect(group.cards[0].className).toBe('border-light');
    expect(group.cards[1].selected).toBe(false);
    expect(group.cards[1].className).toBe('border-light');
    expect(group.cards[2].selected).toBe(true);
    expect(group.cards[2].className).toBe('border-primary');
  });
});
from toxic_tests import Perspective_Handler, monitor_toxicity
from itertools import count

key = 'AIzaSyDQ3mqpqA7hickl44kpKhMHFgDlVvH6bTs'

c = 0
pList = []

# Python Input for Comment Testing
while True:
  text = input()
  if isinstance(text, binary_type):
    text = text.decode('utf-8')

  toxicP = Perspective_Handler(key)
  monitorT = monitor_toxicity()

  # Returns the analyzed comment from the Perspective API
  comment = toxicP.analyze_comment(text)
  # Parse through the Json Dictionaries 
  probs = toxicP.parse_json(comment)
 
  # Calculte Total Prob
  p = monitorT.calculate_tScore(probs)

  # For continuous talk steams
  if p > .85:
    pList.append(p)
    c = c+1
    if c > 1:
      newP = monitorT.calculate_score(c, pList[(c-1)], p)
      print ("Please Remember to Be Kind")


if __name__ == "__main__":
    main()


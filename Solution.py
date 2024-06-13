class Solution:
  def __init__(self,data):
    self.data=data
  def __call__(self,name) -> float:
    return round(self.data.get(name,0))

import streamlit as st
from abc import ABC, abstractmethod

class AuthenticationMenu(ABC):
  @abstractmethod
  def auth(self) -> None:
    pass
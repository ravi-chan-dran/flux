"""Agent implementations for FLUX research system."""

from flux_core.agents.base_agent import BaseAgent
from flux_core.agents.flow_master import FlowMasterAgent
from flux_core.agents.current import CurrentAgent
from flux_core.agents.source import SourceAgent
from flux_core.agents.channel import ChannelAgent
from flux_core.agents.filter import FilterAgent
from flux_core.agents.confluence import ConfluenceAgent

__all__ = [
    "BaseAgent",
    "FlowMasterAgent",
    "CurrentAgent",
    "SourceAgent",
    "ChannelAgent",
    "FilterAgent",
    "ConfluenceAgent",
]


"""Post a Vigil case update into a BAND room. Runs under Python 3.11+ with band-sdk (VIGIL_BAND_PY).
Env: VIGIL_BAND_API_KEY (agent key). Optional VIGIL_BAND_ROOM_ID to reuse a room.
stdin: JSON {"text": "..."}. stdout: JSON evidence. Exit nonzero on any failure. UNVERIFIED until run with a real key."""
import sys, os, json, asyncio
from band.client.rest import AsyncRestClient
from band_rest import ChatRoomRequest, ChatMessageRequest, ChatMessageRequestMentionsItem, ParticipantRequest

async def main():
    text = json.load(sys.stdin)["text"][:800]
    c = AsyncRestClient(api_key=os.environ["VIGIL_BAND_API_KEY"])
    room = os.environ.get("VIGIL_BAND_ROOM_ID")
    if not room:
        r = await c.agent_api_chats.create_agent_chat(chat=ChatRoomRequest(title="Vigil night desk (FICTIONAL)"))
        room = r.data.id
    peers = (await c.agent_api_peers.list_agent_peers(not_in_chat=room)).data
    owner = peers[0] if peers else None
    if owner:
        await c.agent_api_participants.add_agent_chat_participant(room, participant=ParticipantRequest(participant_id=owner.id, role="member"))
        m = ChatMessageRequestMentionsItem(id=owner.id, handle=owner.handle, name=owner.name)
        msg = await c.agent_api_messages.create_agent_chat_message(room, message=ChatMessageRequest(content=f"@{owner.handle} {text}", mentions=[m]))
        print(json.dumps({"room": room, "message_id": getattr(getattr(msg, "data", None), "id", None), "mentioned": owner.handle}))
    else:
        raise RuntimeError("no peer available to @mention")
asyncio.run(main())

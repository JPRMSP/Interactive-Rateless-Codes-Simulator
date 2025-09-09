import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Rateless Codes Simulator", layout="wide")
st.title("Interactive Rateless Codes Simulator")

# ----------------------
# Helper Functions
# ----------------------

def xor_bits(a, b):
    return [x ^ y for x, y in zip(a, b)]

def generate_message(length):
    return [random.randint(0, 1) for _ in range(length)]

def lt_encode(message, num_packets):
    n = len(message)
    packets = []
    for _ in range(num_packets):
        d = np.random.randint(1, n+1)
        indices = random.sample(range(n), d)
        packet = [0]*n
        for idx in indices:
            packet[idx] ^= message[idx]
        packets.append(packet)
    return packets

def simulate_erasure_channel(packets, erasure_prob):
    received = []
    for p in packets:
        if random.random() > erasure_prob:
            received.append(p)
    return received

def lt_decode(received, message_length):
    decoded = [0]*message_length
    packets = received.copy()
    while packets:
        singletons = [p for p in packets if sum(p)==1]
        if not singletons:
            break
        for s in singletons:
            idx = s.index(1)
            decoded[idx] = 1
            packets.remove(s)
            for p in packets:
                if p[idx]==1:
                    p = xor_bits(p, s)
    success = decoded.count(1) == message_length
    return decoded, success

# ----------------------
# User Input
# ----------------------
message_length = st.sidebar.slider("Message Length (bits)", 4, 32, 8)
num_packets = st.sidebar.slider("Number of Encoded Packets", message_length, 2*message_length, message_length)
erasure_prob = st.sidebar.slider("Erasure Probability", 0.0, 1.0, 0.2)

rateless_type = st.sidebar.selectbox("Rateless Code Type", ["LT Code"])

# ----------------------
# Simulation
# ----------------------
message = generate_message(message_length)
st.subheader("Original Message")
st.write(message)

packets = lt_encode(message, num_packets)
st.subheader(f"Encoded Packets ({num_packets})")
st.write(packets)

received = simulate_erasure_channel(packets, erasure_prob)
st.subheader(f"Received Packets after Erasure Channel (p={erasure_prob})")
st.write(received)

decoded, success = lt_decode(received, message_length)
st.subheader("Decoded Message")
st.write(decoded)

if success:
    st.success("Decoding Successful! ✅")
else:
    st.error("Decoding Failed ❌")

st.subheader("Statistics")
st.write({
    "Original Message Length": message_length,
    "Packets Sent": num_packets,
    "Packets Received": len(received),
    "Decoding Successful": success
})

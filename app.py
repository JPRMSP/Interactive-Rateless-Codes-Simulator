import streamlit as st
import numpy as np
import random
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Enhanced Rateless Codes Simulator", layout="wide")
st.title("Enhanced Interactive Rateless Codes Simulator")

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

def raptor_encode(message, num_packets):
    # simple Raptor-like: precode (repeat bits) + LT encode
    precode = [bit for bit in message for _ in range(2)]
    return lt_encode(precode, num_packets)

def simulate_erasure_channel(packets, erasure_prob):
    received = []
    lost_indices = []
    for i, p in enumerate(packets):
        if random.random() > erasure_prob:
            received.append(p)
        else:
            lost_indices.append(i)
    return received, lost_indices

def simulate_noisy_channel(packets, noise_prob):
    noisy_packets = []
    flipped_indices = []
    for p in packets:
        new_p = []
        flipped = []
        for idx, bit in enumerate(p):
            if random.random() < noise_prob:
                new_bit = bit ^ 1
                flipped.append(idx)
            else:
                new_bit = bit
            new_p.append(new_bit)
        noisy_packets.append(new_p)
        flipped_indices.append(flipped)
    return noisy_packets, flipped_indices

def lt_decode(received, message_length):
    decoded = [0]*message_length
    packets = [p.copy() for p in received]
    iterations = 0
    while packets:
        singletons = [p for p in packets if sum(p)==1]
        if not singletons:
            break
        for s in singletons:
            idx = s.index(1)
            decoded[idx] = 1
            packets.remove(s)
            for i, p in enumerate(packets):
                if p[idx]==1:
                    packets[i] = xor_bits(p, s)
        iterations += 1
    success = decoded.count(1) == message_length
    return decoded, success, iterations

# ----------------------
# Sidebar Inputs
# ----------------------
st.sidebar.header("Simulation Parameters")
message_length = st.sidebar.slider("Message Length (bits)", 4, 32, 8)
num_packets = st.sidebar.slider("Number of Encoded Packets", message_length, 2*message_length, message_length)
erasure_prob = st.sidebar.slider("Erasure Probability", 0.0, 1.0, 0.2)
noise_prob = st.sidebar.slider("Noise Probability", 0.0, 0.5, 0.1)
rateless_type = st.sidebar.selectbox("Rateless Code Type", ["LT Code", "Raptor Code"])
channel_type = st.sidebar.selectbox("Channel Type", ["Erasure Channel", "Noisy Channel", "Erasure + Noisy"])

# ----------------------
# Simulation
# ----------------------
message = generate_message(message_length)
st.subheader("Original Message")
st.write(message)

# Encoding
if rateless_type == "LT Code":
    packets = lt_encode(message, num_packets)
else:
    packets = raptor_encode(message, num_packets)

st.subheader(f"Encoded Packets ({num_packets})")
st.dataframe(pd.DataFrame(packets))

# Channel Simulation
if channel_type == "Erasure Channel":
    received, lost = simulate_erasure_channel(packets, erasure_prob)
elif channel_type == "Noisy Channel":
    received, flipped = simulate_noisy_channel(packets, noise_prob)
else:
    temp, lost = simulate_erasure_channel(packets, erasure_prob)
    received, flipped = simulate_noisy_channel(temp, noise_prob)

st.subheader(f"Received Packets after {channel_type}")
st.dataframe(pd.DataFrame(received))

# Decoding
decoded, success, iterations = lt_decode(received, message_length)
st.subheader("Decoded Message")
st.write(decoded)
if success:
    st.success(f"Decoding Successful! ✅ in {iterations} iterations")
else:
    st.error(f"Decoding Failed ❌ after {iterations} iterations")

# Statistics
st.subheader("Simulation Statistics")
stats = {
    "Original Message Length": message_length,
    "Packets Sent": num_packets,
    "Packets Received": len(received),
    "Decoding Successful": success,
    "Decoding Iterations": iterations
}
st.write(stats)

# Plot: Decoding Success vs Number of Packets
success_rates = []
for pkt_count in range(message_length, 2*message_length+1):
    recv, _ = simulate_erasure_channel(packets, erasure_prob)
    _, suc, _ = lt_decode(recv, message_length)
    success_rates.append(suc)
fig = px.line(x=list(range(message_length, 2*message_length+1)), y=success_rates,
              labels={"x":"Packets Sent", "y":"Decoding Success"}, title="Decoding Success vs Packets Sent")
st.plotly_chart(fig)

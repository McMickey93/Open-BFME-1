# 0x008622C0 and 0x00862320: GameSpy `chatConnectA` and `chatConnectSpecialA`

Both 81-byte bodies were rowed as address-named forwarders
(`rva008622C0Forward`, `rva00862320Forward`) in their own TUs. They call
the static `chatConnectDoit` (0x00861ED0), which only links from
`chatMain.c`, so neither TU could link.

## Identity

- Placement: chatMain.c's SDK order is `chatConnectDoit`, `chatConnectA`,
  `chatConnectSpecialA`, `chatConnectSecureA`, `chatConnectLoginA`,
  `chatConnectPreAuthA`. Retail has `chatConnectDoit` 0x00861ED0 (995 B,
  ends 0x008622B3), then 0x008622C0 (81 B), 0x00862320 (81 B), then the
  matched `chatConnectSecureA` 0x00862380 (87 B), `chatConnectLoginA`
  0x008623E0 and `chatConnectPreAuthA` 0x00862460.
- Argument packing: 0x008622C0 passes `CINoLogin` (0), its first five
  arguments as serverAddress/port/nick/user/name, nine zeros
  (namespaceID..secretKey), then callbacks, nickErrorCallback, a zero
  fillInUserCallback, connectCallback, param and blocking. That is SDK
  `chatConnectA`. 0x00862320 passes a zero `user` and forwards a
  fillInUserCallback. That is SDK `chatConnectSpecialA`.
- Open-BFME-2 (same SDK, BFME2 retail): `_chatConnectA` 0x006A31C0/81 and
  `_chatConnectSpecialA` 0x006A3220/81 sit right before
  `_chatConnectSecureA` 0x006A3280/87 in its matched chatMain.c, the same
  sizes and order.
- No rel32 call or ILT jump reaches either body in retail .text, as for an
  unused SDK entry point.

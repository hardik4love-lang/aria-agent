import base64
import json
import subprocess
import os

fixed_code = """import { Tabs, TabsTrigger, TabsList } from '@/components/ui/tabs';

import {
  PieceSelectorTabType,
  usePieceSelectorTabs,
} from '../stores/piece-selector-tabs-provider';
import { ResolvedPieceSelectorTab } from '../utils/piece-selector-customization';

export const PieceSelectorTabs = ({
  tabs,
}: {
  tabs: ResolvedPieceSelectorTab[];
}) => {
  const { selectedTab, selectedCustomTabId, setSelectedTab } =
    usePieceSelectorTabs();
  const selectedTabKey =
    selectedTab === PieceSelectorTabType.CUSTOM
      ? selectedCustomTabId ?? ''
      : selectedTab;
  return (
    <Tabs
      value={selectedTabKey}
      onValueChange={(value) => {
        const tab = tabs.find((candidate) => candidate.key === value);
        if (tab) {
          setSelectedTab(tab.type, tab.customTabId ?? null);
        }
      }}
      className="w-full min-w-0"
    >
      <TabsList
        className={`h-full w-full flex gap-3 px-2 justify-start rounded-none bg-gray-1 overflow-x-auto [&::-webkit-scrollbar]:hidden [scrollbar-width:none]`}
      >
        {tabs.map((tab) => (
          <TabsTrigger
            key={tab.key}
            value={tab.key}
            className={`flex flex-col h-full rounded-md min-w-[85px] px-2.5 shrink-0
              hover:bg-gray-4
               data-[state=active]:text-accent-11 data-[state=active]:shadow-none
               border-transparent data-[state=active]:border-accent-9 data-[state=active]:bg-transparent
               text-gray-12 [&>svg]:size-5 [&>svg]:shrink-0`}
          >
            {tab.icon}
            <span className="mt-1.5 text-sm whitespace-nowrap w-full text-center">
              {tab.name}
            </span>
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
};
"""

b64_content = base64.b64encode(fixed_code.encode("utf-8")).decode("utf-8")

payload = {
    "message": "fix(pieces): prevent piece selector tab labels from truncating (#15039)",
    "content": b64_content,
    "sha": "03a17548eeb40620b9c35b92b26db12f4812719c",
    "branch": "fix/piece-selector-tabs-truncation"
}

temp_file = "D:/aria-agent/scratch/temp_commit_ap.json"
os.makedirs(os.path.dirname(temp_file), exist_ok=True)
with open(temp_file, "w", encoding="utf-8") as f:
    json.dump(payload, f)

cmd = [
    "gh", "api", "--method", "PUT",
    "repos/hardik4love-lang/activepieces/contents/packages/web/src/features/pieces/components/piece-selector-tabs.tsx",
    "--input", temp_file
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Commit status code:", res.returncode)
print("Output:", res.stdout[:300])
if res.returncode != 0:
    print("Error:", res.stderr)
else:
    print("SUCCESS: Fix committed to branch fix/piece-selector-tabs-truncation in hardik4love-lang/activepieces")
